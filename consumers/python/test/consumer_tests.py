import os
import unittest
import pika
from consumers.python.app.rabbit_consumer import RabbitConsumer
from consumers.python.app.rabbit_consumer import RabbitConnectionError
from consumers.python.app.rabbit_consumer import RabbitConsumerError

class TestRabbitConsumer(unittest.TestCase):

    def setUp(self):

        os.environ["RABBIT_USER"] = "localhost"
        os.environ["RABBIT_PASS"] = "dummy"
        os.environ["RABBIT_HOST"] = "dummy"
        os.environ["RABBIT_PORT"] = "5672"
        os.environ["RABBIT_VHOST"] = "dummy"
        os.environ["RABBIT_QUEUE"] = "dummy"

    def test_instantiation(self):

        consumer = RabbitConsumer()
        self.assertEqual(consumer.virtual_host, 'dummy')

    def test_connect(self):

        with self.assertRaises(RabbitConnectionError):
            RabbitConsumer().connect()

    def test_startConsumer(self):

        with self.assertRaises(Exception):
            RabbitConsumer().startConsumer()

    def test_stopConsumer(self):

        with self.assertRaises(Exception):
            RabbitConsumer().stopConsumer()


if __name__=="__main__":
    unittest.main(verbosity=4)
