
PARTE TEORICA

1.1 RabbitMQ

● ¿Qué es RabbitMQ y cuándo conviene usar una cola o un exchange tipo fanout?
RabbitMQ es una herramienta que se usa para enviar mensajes entre distintos servicios, de forma ordenada y sin que tengan que estar conectados directamente. Usamos una cola cuando queremos que solo un servicio reciba y procese un mensaje. En cambio, un exchange tipo fanout cuando queremos que varios servicios reciban el mismo mensaje al mismo tiempo, como en notificaciones o eventos que afectan a varios módulos.

● ¿Qué es una Dead Letter Queue (DLQ) y cómo se configura?
Una DLQ es una cola de mensajes fallidos. Sirve para almacenar los mensajes que no se pudieron procesar correctamente. Para configurarla, solo hay que indicar en la cola original que los mensajes problemáticos se redirijan a otra cola específica, usando parámetros como x-dead-letter-exchange.

1.2 Docker y Docker Compose

● ¿Cuál es la diferencia entre un volumen y un bind mount?
Ambos sirven para guardar datos fuera del contenedor. Un volumen lo administra Docker y se guarda en un lugar reservado por él, para datos que deben mantenerse incluso si se borra el contenedor, como una base de datos. En cambio, un bind mount conecta directamente una carpeta del computador al contenedor, lo que es muy útil en desarrollo, ya que cualquier cambio en los archivos se refleja de inmediato.

● ¿Qué significa usar network_mode: host en un contenedor?
Cuando usamos esa opción, el contenedor comparte la red con el sistema anfitrión, lo que significa que puede usar los mismos puertos y ver los mismos dispositivos de red. Esto puede ser útil para servicios que necesitan un acceso más directo, pero también reduce la separación entre el contenedor y el host, lo que puede ser riesgoso si no se controla bien.

1.3 Traefik

● ¿Para qué sirve Traefik en una arquitectura de microservicios?
Traefik actúa como un reverse proxy y balanceador de carga. Detecta automáticamente los servicios que se levantan y se encarga de redirigir el tráfico hacia ellos. Esto evita tener que configurar manualmente rutas y reglas cada vez que cambia algo.

● ¿Cómo proteger un endpoint con certificados TLS automáticos en Traefik?
Traefik puede generar y renovar certificados SSL/TLS automáticamente usando Let's Encrypt. Se configura con un correo, definir un resolver, y exponer los puertos 80 y 443. Con eso se consigue HTTPS sin tener que preocuparse por actualizar certificados a mano.

PARTE PRACTICA

1. Api funcional
  ![Screenshot 2025-06-03 191052](https://github.com/user-attachments/assets/3b0c11c0-b259-46f5-bd89-addf992ea137)
2. Traefik funcional
   ![Screenshot 2025-06-03 191011](https://github.com/user-attachments/assets/3efbb71d-f704-44d1-9af9-ab4a2c4de215)
3. RabbitMQ funcional
   ![Screenshot 2025-06-03 191110](https://github.com/user-attachments/assets/48bb823b-3159-47b6-b16b-5824b30701d3)
4. Mensajes enviados y recibidos ok
  ![Screenshot 2025-06-03 191154](https://github.com/user-attachments/assets/349f72ba-c7ad-4f55-abac-ae41ec5ad2d3)
5. Health visual
   ![Screenshot 2025-06-03 191656](https://github.com/user-attachments/assets/bce316f9-adcf-4a10-a87a-e5e1ea895806)

