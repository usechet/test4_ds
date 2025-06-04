from flask import Flask, request, jsonify, render_template_string
import pika
import os
import psutil
import datetime
from functools import wraps

app = Flask(__name__)

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>API Message Sender</title>
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
        .form-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #666;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        #response {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
        }
        .success {
            background-color: #dff0d8;
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        .error {
            background-color: #f2dede;
            color: #a94442;
            border: 1px solid #ebccd1;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>API Message Sender</h1>
        <div class="form-group">
            <label for="username">Username:</label>
            <input type="text" id="username" value="admin">
        </div>
        <div class="form-group">
            <label for="password">Password:</label>
            <input type="text" id="password" value="password">
        </div>
        <div class="form-group">
            <label for="message">Message:</label>
            <textarea id="message" rows="4" placeholder="Enter your message here"></textarea>
        </div>
        <button onclick="sendMessage()">Send Message</button>
        <div id="response"></div>
    </div>

    <script>
        function sendMessage() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const message = document.getElementById('message').value;
            const responseDiv = document.getElementById('response');

            // Create Basic Auth header
            const auth = btoa(`${username}:${password}`);

            fetch('/api/message', {
                method: 'POST',
                headers: {
                    'Authorization': `Basic ${auth}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                responseDiv.className = 'success';
                responseDiv.textContent = 'Message sent successfully: ' + JSON.stringify(data);
            })
            .catch(error => {
                responseDiv.className = 'error';
                responseDiv.textContent = 'Error sending message: ' + error.message;
            });
        }
    </script>
</body>
</html>
"""

# HTML Template for health status
HEALTH_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Health Status</title>
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
        .status {
            margin: 20px 0;
            padding: 15px;
            border-radius: 4px;
        }
        .healthy {
            background-color: #dff0d8;
            color: #3c763d;
            border: 1px solid #d6e9c6;
        }
        .metrics {
            margin-top: 20px;
        }
        .metric {
            margin: 10px 0;
            padding: 10px;
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
            margin: 20px 0;
            display: block;
            width: 100%;
        }
        .refresh-button:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Service Health Status</h1>
        <div class="status healthy">
            <h2>Status: {{ health_data.status }}</h2>
        </div>
        <div class="metrics">
            <div class="metric">
                <strong>Uptime:</strong> {{ health_data.uptime }}
            </div>
            <div class="metric">
                <strong>Memory Usage:</strong> {{ health_data.memory_usage }}
            </div>
            <div class="metric">
                <strong>CPU Usage:</strong> {{ health_data.cpu_usage }}%
            </div>
            <div class="metric">
                <strong>RabbitMQ Connection:</strong> {{ health_data.rabbitmq_status }}
            </div>
            <div class="metric">
                <strong>Last Check:</strong> {{ health_data.timestamp }}
            </div>
        </div>
        <button class="refresh-button" onclick="location.reload()">Refresh Status</button>
    </div>
</body>
</html>
"""

# Basic Authentication credentials
AUTH_USERNAME = "admin"
AUTH_PASSWORD = "password"

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    return username == AUTH_USERNAME and password == AUTH_PASSWORD

def authenticate():
    return ('Could not verify your access level for that URL.\n'
            'You have to login with proper credentials', 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'})

def get_rabbitmq_connection():
    credentials = pika.PlainCredentials(
        os.environ.get('RABBITMQ_USER', 'guest'),
        os.environ.get('RABBITMQ_PASSWORD', 'guest')
    )
    parameters = pika.ConnectionParameters(
        host=os.environ.get('RABBITMQ_HOST', 'localhost'),
        credentials=credentials
    )
    return pika.BlockingConnection(parameters)

@app.route('/')
def root():
    return render_template_string(HTML_TEMPLATE)

@app.route('/message', methods=['POST'])
@require_auth
def publish_message():
    if not request.is_json:
        return jsonify({"error": "Content type must be application/json"}), 400
    
    message = request.get_json()
    
    try:
        connection = get_rabbitmq_connection()
        channel = connection.channel()
        
        # Declare the queue
        channel.queue_declare(queue='messages')
        
        # Publish message
        channel.basic_publish(
            exchange='',
            routing_key='messages',
            body=str(message)
        )
        
        connection.close()
        return jsonify({"status": "Message published successfully"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health_check():
    # Get system metrics
    process = psutil.Process(os.getpid())
    
    # Check RabbitMQ connection
    try:
        connection = get_rabbitmq_connection()
        connection.close()
        rabbitmq_status = "Connected"
    except:
        rabbitmq_status = "Disconnected"

    health_data = {
        "status": "healthy",
        "uptime": str(datetime.timedelta(seconds=int(process.create_time() - psutil.boot_time()))),
        "memory_usage": f"{process.memory_info().rss / 1024 / 1024:.2f} MB",
        "cpu_usage": f"{process.cpu_percent(interval=1):.1f}",
        "rabbitmq_status": rabbitmq_status,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Return JSON if requested via API
    if request.headers.get('Accept') == 'application/json':
        return jsonify(health_data)

    # Return HTML for browser
    return render_template_string(HEALTH_TEMPLATE, health_data=health_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 