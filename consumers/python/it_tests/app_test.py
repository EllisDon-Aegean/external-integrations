import os
import unittest
from consumers.python.app.app import App

class AppTest(unittest.TestCase):

    def setUp(self):

        os.environ["RABBIT_USER"] = "client"
        os.environ["RABBIT_PASS"] = "guest"
        os.environ["RABBIT_HOST"] = "localhost" 
        os.environ["RABBIT_PORT"] = "5672"
        os.environ["RABBIT_VHOST"] = "/client"
        os.environ["RABBIT_QUEUE"] = "client.dev.v1"

    def testApp(self):

        app = App()
        app.startApp()


if __name__=="__main__":
    unittest.main(verbosity=4)
