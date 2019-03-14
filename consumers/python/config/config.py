import os

def setConfig():
    os.environ["RABBIT_USER"] = "client"
    os.environ["RABBIT_PASS"] = "guest"
    #os.environ["RABBIT_HOST"] = "ec2-54-86-251-228.compute-1.amazonaws.com"
    os.environ["RABBIT_HOST"] = "rabbit"
    os.environ["RABBIT_PORT"] = "5672"
    os.environ["RABBIT_VHOST"] = "/client"
    os.environ["RABBIT_QUEUE"] = "client.dev.v1"
