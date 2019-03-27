import os

def setConfig():
    os.environ["RABBIT_USER"] = "ellisdon"
    os.environ["RABBIT_PASS"] = "guest"
    os.environ["RABBIT_HOST"] = "rabbit"
    os.environ["RABBIT_PORT"] = "5672"
    os.environ["RABBIT_VHOST"] = "/ellisdon"
    os.environ["RABBIT_QUEUE"] = "ellisdon.dev.v1"
    os.environ["RABBIT_ROUTING"] = "ellisdon.direct"
    os.environ["RABBIT_EXCHANGE"] = "ellisdon_exchange"
