import os
import sys
from consumers.python.app.base_consumer import BaseConsumer
from consumers.python.app.base_consumer import BaseConnectionError
from consumers.python.app.base_consumer import BaseConsumerError

class AppAsync:

    def __init__(self):
        self.consumer = None

    def startApp(self):
        try:
            self.consumer = BaseConsumer()
            self.consumer.asyncConnect()
            self.consumer.startAsyncConsumer()
        except Exception as e:
            raise Exception("Async consumer failed to start") from e
