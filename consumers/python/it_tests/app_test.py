import os
import unittest
from consumers.python.app.app import App

class AppTest(unittest.TestCase):

    def setUp(self):
        os.environ.update({
            "RABBIT_USER": "client",
            "RABBIT_PASS": "guest",
            "RABBIT_HOST": os.environ.get("EXT_SERVER", "localhost"),
            "RABBIT_PORT": "5672",
            "RABBIT_VHOST": "/client",
            "RABBIT_QUEUE": "integration",
            "RABBIT_ROUTING": "client.prequal",
            "RABBIT_EXCHANGE": "integration"
        })

    def testApp(self):
        app = App()
        app.startApp()


if __name__=="__main__":
    unittest.mainverbosity=4
