import os
import time
import unittest
from consumers.python.app.app_async import AppAsync

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
        app = AppAsync()
        app.startApp()

if __name__=="__main__":
    unittest.main(verbosity=4)
