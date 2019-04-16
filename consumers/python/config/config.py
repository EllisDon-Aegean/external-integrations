import os

def setConfig():
    os.environ.update({
        "RABBIT_USER": "client",
        "RABBIT_PASS": "guest",
        "RABBIT_HOST": "rabbit",
        "RABBIT_PORT": "5672",
        "RABBIT_VHOST": "/client",
        "RABBIT_QUEUE": "integration",
        "RABBIT_ROUTING": "client.prequal",
        "RABBIT_EXCHANGE": "integration"
    })
