import os
import sys
from consumers.python.app.rabbit_consumer import RabbitConsumer
from consumers.python.app.rabbit_consumer import RabbitConnectionError
from consumers.python.app.rabbit_consumer import RabbitConsumerError

class AppAsync:

    def __init__(self):
        self.consumer = None

    def startApp(self):
        try:
            self.consumer = RabbitConsumer()
            self.consumer.asyncConnect()
            self.consumer.startAsyncConsumer()
        except Exception as e:
            print(e)
