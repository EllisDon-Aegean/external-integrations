import pika
import os

class RabbitConnectionError(Exception):
    pass

class RabbitConsumerError(Exception):
    pass

MAX_RECONNECTION_ATTEMPT = 5

class RabbitConsumer:

    def __init__(self):
        self.connecion = None
        self.channel = None
        self.async_connection = None
        self.async_channel = None
        self.connection_attempt = 0
        self.async_connection_attempt = 0
        self.shutting_down = False
        self.user = os.environ.get("RABBIT_USER", None)
        self.password = os.environ.get("RABBIT_PASS", None)
        self.host = os.environ.get("RABBIT_HOST", None)
        self.virtual_host = os.environ.get("RABBIT_VHOST", None)
        self.queue = os.environ.get("RABBIT_QUEUE", None)
        self.exchange = os.environ.get("RABBIT_EXCHANGE", None)
        self.routing_key = os.environ.get("RABBIT_ROUTING", None)
        try:
            self.port= int(os.environ.get("RABBIT_PORT", "5672"))
        except ValueError:
            raise ValueError("Check port number")
        if self.user is None or self.virtual_host is None or self.host is None:
            raise Exception("RabbitMQ consumer failed to initialize host/ virtual_host/ user")

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
                connection_attempts=MAX_RECONNECTION_ATTEMPT,
                retry_delay=5
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        except Exception as e:
            raise RabbitConnectionError("RabbitMQ BlockingConnection failed to connect") from e

    def asyncConnect(self):
        print("connecting async client")
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
                connection_attempts=MAX_RECONNECTION_ATTEMPT,
                retry_delay=5
            )
            print("Opening connection")
            self.async_connection = pika.SelectConnection(
                parameters,
                self.on_connection_open,
                stop_ioloop_on_close=False
            )
            print(self.async_connection)
            self.add_on_connection_close_callback()
        except Exception as e:
            raise RabbitConnectionError("RabbitMQ SelectConnection Failed to connect") from e

    def on_connection_open(self, connection):
        self.async_connection = connection
        print("opening channel")
        connection.channel(self.on_channel_open)

    def add_on_connection_close_callback(self):
        print('Adding connection close callback')
        self.async_connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self.async_channel = None
        if self.shutting_down:
            self.async_connection.ioloop.stop()
        else:
            print('Connection closed, reopening in 5 seconds: (%s) %s',
                           reply_code, reply_text)
            self.async_connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        # This is the old connection IOLoop instance, stop its ioloop
        print("Stopping existing io loop")
        self.async_connection.ioloop.stop()
        # Create a new connection
        self.asyncConnect()
        # There is now a new connection, needs a new ioloop to run
        self.async_connection.ioloop.start()

    def add_on_channel_close_callback(self):
        print('Adding channel close callback')
        self.async_channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        print('Channel was closed: (%s) %s', reply_code, reply_text)
        if not self.shutting_down:
            self.async_connection.close()

    def on_channel_open(self, channel):
        self.async_channel = channel
        self.add_on_channel_close_callback()
        print("Declaring Queue")
        channel.queue_declare(
            callback=self.on_queue_declareok,
            queue=self.queue,
            durable=True
        )

    def acknowledgeMsg(self, ch, basic_deliver, properties, body):
        print('Received message # %s from %s: %s',
                    basic_deliver.delivery_tag, properties.app_id, body)
        ch.basic_ack(delivery_tag = basic_deliver.delivery_tag)

    def on_queue_declareok(self, method_frame):
        print('Binding %s to %s with %s',
                    self.exchange, self.queue, self.routing_key)
        self.async_channel.queue_bind(self.on_bindok, self.queue,
                                 self.exchange, self.routing_key)

    def on_bindok(self, unused_frame):
        print('Rabbit Queue bound')
        self.async_channel.basic_consume(
            self.acknowledgeMsg,
            queue=self.queue
        )

    def startAsyncConsumer(self):
        print("Starting RabbitMQ consumer")
        try:
            self.async_connection.ioloop.start()
        except KeyboardInterrupt:
            self.shutting_down = True
            self.async_channel.close()
            self.async_connection.close()
        except Exception as e:
            raise RabbitConnectionError("Async Consumer encountered error") from e

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
                self.channel.stop_consuming()
                self.connection.close()
            except pika.exceptions.ConnectionClosed as e:
                print(e)
                print("Connection closed: Reconnecting in 5 seconds")
                time.sleep(5)
                self.connect()
                self.startBlockingConsumer()
            except Exception as e:
                raise RabbitConsumerError("Blcoking consumer failed to start") from e
        else:
            raise RabbitConnectionError("Channel not instantiated")

    def closeAsyncConsumer(self):
        try:
            self.async_channel.close()
            self.async_connection.close()
        except Exception as e:
            raise RabbitConsumerError("Async consumer graceful shutdown failed")

    def stopConsumer(self):
        if self.channel:
            try:
                self.channel.basic_cancel()
            except Exception as e:
                raise RabbitConsumerError from e
        else:
            raise Exception("Channel not instantiated: No consumer")

    def onStopConsumer(self):
        self.closeChannel()

    def closeChannel(self):
        if self.channel:
            try:
                self.channel.close()
            except Exception as e:
                raise RabbitConnectionError from e
        else:
            raise Exception("Cannot close uninstantiated channel")

    def closeConnection(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                raise RabbitConnectionError from e
        else:
            raise Exception("No connection exists")
