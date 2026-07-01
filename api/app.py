from http.server import BaseHTTPRequestHandler
import pika, os, json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. Pega o segredo
        url = os.environ.get('RABBITMQ_URL')
        if not url:
            self.send_response(500)
            self.end_headers()
            self.wfile.write('Falta a URL do RabbitMQ!'.encode('utf-8'))
            return

        # 2. Conecta no CloudAMQP
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='scraping_tasks', durable=True)

        # 3. Prepara as tarefas
        sites = [
            {'url': 'https://g1.globo.com/tecnologia/', 'fonte': 'G1 Tecnologia'},
            {'url': 'https://techcrunch.com/', 'fonte': 'TechCrunch'}
        ]

        # 4. Envia para a fila
        for site in sites:
            mensagem = json.dumps(site)
            channel.basic_publish(
                exchange='',
                routing_key='scraping_tasks',
                body=mensagem,
                properties=pika.BasicProperties(delivery_mode=2)
            )

        connection.close()
        
        # 5. Responde para a Vercel que deu tudo certo
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('Tarefas enviadas com sucesso para a fila!'.encode('utf-8'))
