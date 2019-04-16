import pika
import os

class BaseConnectionError(Exception):
    pass

class BaseConsumerError(Exception):
    pass

MAX_RECONNECTION_ATTEMPT = 5

class BaseConsumer:

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
        except ValueError as ve:
            raise BaseConsumerError("Check port number") from ve
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
            raise BaseConnectionError("RabbitMQ BlockingConnection failed to connect") from e

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
                connection_attempts=MAX_RECONNECTION_ATTEMPT,
                retry_delay=5
            )
            self.async_connection = pika.SelectConnection(
                parameters,
                self.on_connection_open,
                stop_ioloop_on_close=False
            )
            self.add_on_connection_close_callback()
        except Exception as e:
            raise BaseConnectionError("RabbitMQ SelectConnection Failed to connect") from e

    def on_connection_open(self, connection):
        self.async_connection = connection
        connection.channel(self.on_channel_open)

    def add_on_connection_close_callback(self):
        self.async_connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_closed(self, connection, reply_code, reply_text):
        self.async_channel = None
        if self.shutting_down:
            self.async_connection.ioloop.stop()
        else:
            self.async_connection.add_timeout(5, self.reconnect)

    def reconnect(self):
        self.async_connection.ioloop.stop()
        self.asyncConnect()
        self.async_connection.ioloop.start()

    def add_on_channel_close_callback(self):
        self.async_channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reply_code, reply_text):
        if not self.shutting_down:
            self.async_connection.close()

    def on_channel_open(self, channel):
        self.async_channel = channel
        self.add_on_channel_close_callback()
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
        self.async_channel.queue_bind(self.on_bindok, self.queue,
                                 self.exchange, self.routing_key)

    def on_bindok(self, unused_frame):
        self.async_channel.basic_consume(
            self.acknowledgeMsg,
            queue=self.queue
        )

    def startAsyncConsumer(self):
        try:
            self.async_connection.ioloop.start()
        except KeyboardInterrupt:
            self.shutting_down = True
            self.async_channel.close()
            self.async_connection.close()
        except Exception as e:
            raise BaseConnectionError("Async Consumer encountered error") from e

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
                self.channel.start_consuming()
            except KeyboardInterrupt:
                self.channel.stop_consuming()
                self.connection.close()
            except pika.exceptions.ConnectionClosed as e:
                time.sleep(5)
                self.connect()
                self.startBlockingConsumer()
            except Exception as e:
                raise BaseConsumerError("Blcoking consumer failed to start") from e
        else:
            raise BaseConnectionError("Channel not instantiated")

    def closeAsyncConsumer(self):
        try:
            self.async_channel.close()
            self.async_connection.close()
        except Exception as e:
            raise BaseConsumerError("Async consumer graceful shutdown failed")

    def stopConsumer(self):
        if self.channel:
            try:
                self.channel.basic_cancel()
            except Exception as e:
                raise BaseConsumerError from e
        else:
            raise Exception("Channel not instantiated: No consumer")

    def onStopConsumer(self):
        self.closeChannel()

    def closeChannel(self):
        if self.channel:
            try:
                self.channel.close()
            except Exception as e:
                raise BaseConnectionError from e
        else:
            raise Exception("Cannot close uninstantiated channel")

    def closeConnection(self):
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                raise BaseConnectionError from e
        else:
            raise Exception("No connection exists")
