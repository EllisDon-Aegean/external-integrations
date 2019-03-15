import os
import time
import unittest
from consumers.python.app.app_async import AppAsync

class AppTest(unittest.TestCase):

    def setUp(self):

        os.environ["RABBIT_USER"] = "client"
        os.environ["RABBIT_PASS"] = "guest"
        os.environ["RABBIT_HOST"] = "localhost"
        os.environ["RABBIT_PORT"] = "5672"
        os.environ["RABBIT_VHOST"] = "/client"
        os.environ["RABBIT_QUEUE"] = "client.dev.v1"
        os.environ["RABBIT_ROUTING"] = "fanout"
        os.environ["RABBIT_EXCHANGE"] = "client.fanout"

    def testApp(self):

        app = AppAsync()
        app.startApp()
        time.sleep(3)
        app.stopApp()

if __name__=="__main__":
    unittest.main(verbosity=4)
