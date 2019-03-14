# Integration Repo

 This repository serves as the hub for all integration pieces for third party.

# Python Consumer

 ## Getting Started 
 
`Docker` is required for running the local `RabbitMQ` server and the connector app. `Docker` can be either run natively like OSX native `Docker` desktop or via using the `Docker-Machine`. 

## Setup

Run `source setup_consumers.sh` for running the RabbitMQ server and the python consumer.
Run `sh teardown_consumer.sh` for shutting down everything.

## Local vs Remote RabbitMQ Server

The docker environment varibles are set to local RabbitMQ server. 

RabbitMQ connection parameters can be changed by setting the varibles in the file
`/consumers/python/config/config.py`. For example:

```
def setConfig():
    os.environ["RABBIT_USER"] = "client"
    os.environ["RABBIT_PASS"] = "guest"
    os.environ["RABBIT_HOST"] = "rabbit"
    os.environ["RABBIT_PORT"] = "5672"
    os.environ["RABBIT_VHOST"] = "/client"
    os.environ["RABBIT_QUEUE"] = "client.dev.v1"
```

For a remote consumer, these variables will need to be set to remote host.

## Unit Testing

There is one unit test suite for checking exceptions for RabbitConsumer class.
Run `python -m consumers.python.test.consumer_tests`.

## Integration Testing

Integration testing requires an active RabbitMQ connection. One way to achieve that
is to test it using the local RabbitMQ server. Currently, the integration test
connection parameters are set to local rabbit host.


