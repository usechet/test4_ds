import pika
import os
import json
from datetime import datetime
from flask import Flask, render_template_string
from threading import Thread

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Message Viewer</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .messages {
            margin-top: 20px;
        }
        .message {
            padding: 10px;
            margin-bottom: 10px;
            background-color: #f8f9fa;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .refresh-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 20px;
        }
        .refresh-button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Messages Log Viewer</h1>
        <button class="refresh-button" onclick="location.reload()">Refresh Messages</button>
        <div class="messages">
            {% for message in messages %}
            <div class="message">{{ message }}</div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.environ.get('RABBITMQ_USER', 'guest'),
        os.environ.get('RABBITMQ_PASSWORD', 'guest')
    )
    parameters = pika.ConnectionParameters(
        host=os.environ.get('RABBITMQ_HOST', 'localhost'),
        credentials=credentials,
        connection_attempts=10,
        retry_delay=5
    )
    return pika.BlockingConnection(parameters)

def callback(ch, method, properties, body):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    message = f"[{timestamp}] {body.decode()}\n"
    
    with open('/app/data/messages.log', 'a') as f:
        f.write(message)
    
    print(f"Message received and saved: {message}")
    ch.basic_ack(delivery_tag=method.delivery_tag)

@app.route('/')
def view_messages():
    try:
        with open('/app/data/messages.log', 'r') as f:
            messages = f.readlines()
    except FileNotFoundError:
        messages = []
    return render_template_string(HTML_TEMPLATE, messages=messages)

def run_flask():
    app.run(host='0.0.0.0', port=8000)

def run_worker():
    os.makedirs('/app/data', exist_ok=True)
    
    connection = get_rabbitmq_connection()
    channel = connection.channel()
    
    channel.queue_declare(queue='messages')
    
    channel.basic_consume(
        queue='messages',
        on_message_callback=callback
    )
    
    print('Worker started. Waiting for messages...')
    channel.start_consuming()

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = Thread(target=run_flask)
    flask_thread.start()
    
    # Run the worker in the main thread
    run_worker() 