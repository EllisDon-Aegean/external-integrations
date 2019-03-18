import os
import sys
from consumers.python.app.rabbit_consumer import RabbitConsumer
from consumers.python.app.rabbit_consumer import RabbitConnectionError
from consumers.python.app.rabbit_consumer import RabbitConsumerError

class App:

    def __init__(self):
        self.consumer = None

    def startApp(self):

        try:
            self.consumer = RabbitConsumer()
            self.consumer.connect()
            self.consumer.startBlockingConsumer()
        except RabbitConnectionError as e:
            print(e)
        except RabbitConsumerError as e:
            print(e)
        except Exception as e:
            print(e)

    def stopApp(self):

        try:
            self.consumer.stopConsumer()
            self.consumer.closeChannel
            self.consumer.closeConnection()
        except Exception as e:
            print(e)
