import pika
import os

class RabbitConnectionError(Exception):
    pass

class RabbitConsumerError(Exception):
    pass

class RabbitConsumer:

    def __init__(self):

        self.connection = None
        self.channel = None
        self.async_connection = None
        self.async_channel = None

        try:
            self.user = os.environ['RABBIT_USER']
            self.password = os.environ['RABBIT_PASS']
            self.host = os.environ['RABBIT_HOST']
            self.port= int(os.environ['RABBIT_PORT'])
            self.virtual_host = os.environ['RABBIT_VHOST']
            self.queue = os.environ['RABBIT_QUEUE']
            self.exchange = os.environ['RABBIT_EXCHANGE']
            self.routing_key = os.environ['RABBIT_ROUTING']
        except KeyError:
            raise KeyError("Environment Variables Not Set")


    def acknowledgeMsg(self, ch, method, properties, body):

        print("Rabbit Msg Received %r" % body)
        ch.basic_ack(delivery_tag = method.delivery_tag)


    def connect(self):

        try:
            credentials = pika.PlainCredentials(
                self.user,
                self.password
            )
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                connection_attempts=5,
                retry_delay=5
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        except Exception as e:
            print(e)
            raise RabbitConnectionError


    def asyncConnect(self):

        try:
            credentials = pika.PlainCredentials(
                self.user,
                self.password
            )
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                connection_attempts=5,
                retry_delay=5
            )
            print("Opening connection")
            connection = pika.SelectConnection(
                parameters,
                self.on_connection_open
            )
            self.async_connection = connection
        except Exception as e:
            print(e)
            raise RabbitConnectionError


    def on_connection_open(self, connection):

        self.async_connection = connection
        print("opening channel")
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):

        self.async_channel = channel
        print("Declaring Queue")
        channel.queue_declare(
            callback=self.on_queue_declareok,
            queue=self.queue,
            durable=True
        )
        channel.basic_consume(
            self.acknowledgeMsg,
            queue=self.queue
        )

    def on_queue_declareok(self, method_frame):

        print('Binding %s to %s with %s',
                    self.exchange, self.queue, self.routing_key)
        self.async_channel.queue_bind(self.on_bindok, self.queue,
                                 self.exchange, self.routing_key)

    def on_bindok(self, unused_frame):
        print('Queue bound')


    def startAsyncConsumer(self):

        print("Starting RabbitMQ consumer")
        try:
            self.async_connection.ioloop.start()
        except Exception as e:
            print(e)
            raise RabbitConnectionError("Async consumer failed to start")


    def startBlockingConsumer(self):

        if self.channel:
            try:
                self.channel.queue_declare(
                    queue=self.queue,
                    durable=True
                )
                self.channel.basic_consume(
                    self.acknowledgeMsg,
                    queue=self.queue
                )
                print("Starting RabbitMQ consumer")
                self.channel.start_consuming()
            except KeyboardInterrupt:
                print("Received keyboard interrupt, closing consuner")
                self.channel.stop_consuming()
                self.connection.close()
            except Exception as e:
                print(e)
                raise RabbitConsumerError
        else:
            raise Exception("Channel not instantiated")


    def stopConsumer(self):

        if self.channel:
            try:
                self.channel.basic_cancel()
            except Exception as e:
                print(e)
                raise RabbitConsumerError
        else:
            raise Exception("Channel not instantiated: No consumer")

    def onStopConsumer(self):

        print("Closing RabbitMQ Consumer")
        self.closeChannel()


    def closeChannel(self):

        if self.channel:
            try:
                print("Closing channel")
                self.channel.close()
            except Exception as e:
                print(e)
                raise RabbitConnectionError
        else:
            raise Exception("Cannot close uninstantiated channel")


    def closeConnection(self):

        if self.connection:
            try:
                print("Closing Connection")
                self.connection.close()
            except Exception as e:
                print(e)
                raise e
        else:
            raise Exception("No connection exists")
