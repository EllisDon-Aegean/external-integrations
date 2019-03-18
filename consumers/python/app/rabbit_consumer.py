import pika
import os
import time

class RabbitConnectionError(Exception):
    pass

class RabbitConsumerError(Exception):
    pass

MAX_RECONNECTION_ATTEMPT = 20

class RabbitConsumer:

    def __init__(self):

        self.connecion = None
        self.channel = None
        self.async_connection = None
        self.async_channel = None

        self.connection_attempt = 0
        self.shutting_down = False

        try:
            self.user = os.environ.get("RABBIT_USER", "")
            self.password = os.environ.get("RABBIT_PASS", "")
            self.host = os.environ.get("RABBIT_HOST", "")
            self.port= int(os.environ.get("RABBIT_PORT", "5672"))
            self.virtual_host = os.environ.get("RABBIT_VHOST", "")
            self.queue = os.environ.get("RABBIT_QUEUE", "")
            self.exchange = os.environ.get("RABBIT_EXCHANGE", "")
            self.routing_key = os.environ.get("RABBIT_ROUTING", "")
        except ValueError:
            raise ValueError("Check port number")


    def acknowledgeMsg(self, ch, method, properties, body):

        print("Rabbit Msg Received %r" % body)
        ch.basic_ack(delivery_tag = method.delivery_tag)


    def connect(self):

        if self.connection_attempt > MAX_RECONNECTION_ATTEMPT:
            raise Exception("Max reconnection attempt exceeded: exiting")
        try:
            self.connection_attempt += 1
            credentials = pika.PlainCredentials(
                self.user,
                self.password
            )
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                connection_attempts=10,
                retry_delay=5
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
        except Exception as e:
            print(e)
            raise RabbitConnectionError


    def asyncConnect(self):

        if self.connection_attempt > MAX_RECONNECTION_ATTEMPT:
            raise Exception("Max reconnection attempt exceeded: exiting")

        print("connecting async client")
        try:
            self.connection_attempt += 1
            credentials = pika.PlainCredentials(
                self.user,
                self.password
            )
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.virtual_host,
                credentials=credentials,
                connection_attempts=10,
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
            print(e)
            raise RabbitConnectionError("Failed to connect")


    def on_connection_open(self, connection):

        self.async_connection = connection
        self.connection_attempt = 0
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
            time.sleep(5)
            self.reconnect()


    def reconnect(self):

        self._deliveries = []
        self._acked = 0
        self._nacked = 0
        self._message_number = 0

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
        except KeyboardInterrupt:
            print("Received keyboard interrupt, closing consumer")
            self.shutting_down = True
            self.async_channel.close()
            self.async_connection.close()
            print("Closed rabbit consumer")
        except Exception as e:
            print(e)
            raise RabbitConnectionError("Async Consumer encountered error")


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
                self.connection_attempt = 0
                self.channel.start_consuming()
            except KeyboardInterrupt:
                print("Received keyboard interrupt, closing consumer")
                self.channel.stop_consuming()
                self.connection.close()
            except pika.exceptions.ConnectionClosed as e:
                print(e)
                print("Connection closed: Reconnecting in 5 seconds")
                time.sleep(5)
                self.connect()
                self.startBlockingConsumer()
            except Exception as e:
                print(e)
                raise RabbitConsumerError("Blcoking consumer failed to start")
        else:
            raise RabbitConnectionError("Channel not instantiated")


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
