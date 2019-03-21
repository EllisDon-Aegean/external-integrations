import os
import unittest
from consumers.python.app.app import App

class AppTest(unittest.TestCase):

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

    def testApp(self):
        app = App()
        app.startApp()


if __name__=="__main__":
    unittest.mainverbosity=4
