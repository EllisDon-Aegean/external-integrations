import os
import unittest
import pika
from consumers.python.app.rabbit_consumer import RabbitConsumer
from consumers.python.app.rabbit_consumer import RabbitConnectionError
from consumers.python.app.rabbit_consumer import RabbitConsumerError

class TestRabbitConsumer(unittest.TestCase):

    def setUp(self):
        os.environ.update({
            "RABBIT_USER": "client",
            "RABBIT_PASS": "guest",
            "RABBIT_HOST": "localhost",
            "RABBIT_PORT": "5672",
            "RABBIT_VHOST": "/client",
            "RABBIT_QUEUE": "client.dev.v1",
            "RABBIT_ROUTING": "fanout",
            "RABBIT_EXCHANGE": "client.fanout"
        })

    def test_instantiation(self):
        consumer = RabbitConsumer()
        self.assertEqual(consumer.virtual_host, 'dummy')

    def test_connect(self):
        with self.assertRaises(RabbitConnectionError):
            RabbitConsumer().connect()

    def test_startConsumer(self):
        with self.assertRaises(Exception):
            RabbitConsumer().startBlockingConsumer()

    def test_stopConsumer(self):
        with self.assertRaises(Exception):
            RabbitConsumer().stopConsumer()


if __name__=="__main__":
    unittest.main(verbosity=4)
