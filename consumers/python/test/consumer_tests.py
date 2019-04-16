import os
import unittest
import pika
from consumers.python.app.base_consumer import BaseConsumer
from consumers.python.app.base_consumer import BaseConnectionError
from consumers.python.app.base_consumer import BaseConsumerError

class TestBaseConsumer(unittest.TestCase):

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
        consumer = BaseConsumer()
        self.assertEqual(consumer.virtual_host, '/client')

    def test_connect(self):
        with self.assertRaises(BaseConnectionError):
            BaseConsumer().connect()

    def test_startConsumer(self):
        with self.assertRaises(Exception):
            BaseConsumer().startBlockingConsumer()

    def test_stopConsumer(self):
        with self.assertRaises(Exception):
            BaseConsumer().stopConsumer()


if __name__=="__main__":
    unittest.main(verbosity=4)
