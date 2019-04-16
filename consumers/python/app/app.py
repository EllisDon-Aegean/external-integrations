import os
import sys
from consumers.python.app.base_consumer import BaseConsumer
from consumers.python.app.base_consumer import BaseConnectionError
from consumers.python.app.base_consumer import BaseConsumerError

class App:

    def __init__(self):
        self.consumer = None

    def startApp(self):
        try:
            self.consumer = BaseConsumer()
            self.consumer.connect()
            self.consumer.startBlockingConsumer()
        except Exception as e:
            raise Exception("Blocking consumer failed to start") from e

    def stopApp(self):
        try:
            self.consumer.stopConsumer()
            self.consumer.closeChannel
            self.consumer.closeConnection()
        except Exception as e:
            raise Exception("Blocking consumer failed to stop gracefully") from e
