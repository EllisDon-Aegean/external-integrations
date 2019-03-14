import pika
import os

host = os.environ["DOCKER_MACHINE_IP"]
credentials = pika.PlainCredentials('client', 'guest')
parameters = pika.ConnectionParameters(host, 5672, '/client', credentials)

connection = pika.BlockingConnection(parameters)

channel = connection.channel()

example = "Rabbit Msg "

channel.queue_declare(queue='client.dev.v1',durable=True)

for i in range(0, 100):
    body = example + str(i)
    channel.basic_publish(exchange='client.fanout',routing_key='fanout',body=body)

connection.close()
