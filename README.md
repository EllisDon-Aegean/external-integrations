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
```

For a remote consumer, these variables will need to be set to remote host.

## Unit Testing

There is one unit test suite for checking exceptions for RabbitConsumer class.
Run `python -m consumers.python.test.consumer_tests`.

## Integration Testing

Integration testing requires an active RabbitMQ connection. One way to achieve that
is to test it using the local RabbitMQ server. Currently, the integration test
connection parameters are set to local rabbit host.

## Data Payloads

# Submission Data
Submission data refers to business, finance and health safety data. Following is the example:
```{
            "tax_number": 123456789,
            "files": ["finance_file.txt", "finance_file2.pdf"],
            "status": "in_review",
            "sub_name": "Subcontractor",
            "event": "submission.finance"
}```

`sub_name` refers to subcontractor name.

# Prequalification Data
```{
            "single_contract_limit": 1234515698.0,
            "aggregate_contract_limit": 12315867912.0,
            "expiry": 156729456,
            "tax_number": 12315627128,
            "sub_name": "Subcontractor",
            "event": "prequalification.post"
}```

Here expiry timestamp is the unix timestamp.

# Score Data
This event is published when Q score is updated:
```{
                "q_score": 1.3,
                "prequalification": {},
                "sub_name": "subcontractor",
                "event": "score.update"
}```
Here the prequalification refers to the prequalification data containing 
all the fields in `Prequalification Data` section except the `event` field.
q_score field refers to the calculated Q score for respective subcontractor.

