from load_balancer.client import Client
from load_balancer.broker import ExecutionBroker as Broker

def test_handle_frontend():
    broker = Broker()
    client = Client()
    assert not broker.queue
    client.submit_jobs(["test"])
    broker.handle_frontend_message()
    assert b"test" in broker.queue
