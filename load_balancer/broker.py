import zmq
import random
import time
import logging

TIMEOUT = 10
context = zmq.Context()

class ExecutionBroker:

    def __init__(self):
        """commands - shell commands to execute."""

        # Socket to send messages on
        self.backend = context.socket(zmq.ROUTER)
        self.backend.bind("tcp://*:5557")
        self.frontend = context.socket(zmq.ROUTER)
        self.frontend.bind("tcp://*:5558")
        self.queue = []
        self._workers = {}
        self.available_workers = []

        self.poller = zmq.Poller()
        self.poller.register(self.backend, zmq.POLLIN)
        self.poller.register(self.frontend, zmq.POLLIN)

    def handle_backend_message(self):

        backend = self.backend
        address, _, msg = backend.recv_multipart()
        workers = self._workers
        available_workers = self.available_workers

        current_time = time.time()
        if msg == b'READY':
            workers.pop(address, None)
            logging.debug("worker {} ready".format(address))
            available_workers.append(address)

        elif msg == b'ALIVE':
            if address in workers:
                workers[address]['last_seen'] = current_time

    def handle_frontend_message(self):
        frontend = self.frontend
        workers = self._workers

        client, _, payload = frontend.recv_multipart()
        self.queue.append(payload)


    def handle_queue(self):
        queue = self.queue
        available_workers = self.available_workers
        workers = self._workers

        current_time = time.time()
        while queue and available_workers:
            worker = self.available_workers.pop(0)
            payload = queue.pop(0)

            workers[worker] = {'payload': payload, 'last_seen': current_time}
            self.backend.send_multipart([worker, b'', payload])
            logging.debug("Sending payload:", payload)


    def _event_loop(self):

        workers = self._workers
        queue = self.queue
        backend = self.backend
        frontend = self.frontend
        available_workers = self.available_workers
        poller = self.poller

        while True:
            sockets = dict(poller.poll(timeout=100))

            if backend in sockets:
                self.handle_backend_message()

            if frontend in sockets:
                self.handle_frontend_message()

            self.handle_queue()

            self._check_alive()


    def _check_alive(self):
        workers = self._workers
        queue = self.queue

        current_time = time.time()

        for addr in list(workers):
            worker_info = workers[addr]
            if worker_info['last_seen'] + TIMEOUT < current_time:
                logging.debug("worker dead, need to restart with payload: %s", worker_info['payload'])
                workers.pop(addr)
                queue.append(worker_info['payload'])


    def run(self):

        # run main event loop
        self._event_loop()

if __name__ == '__main__':

    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--loglevel', choices=['DEBUG', 'ERROR', 'CRITICAL', 'WARNING', 'INFO'], default='INFO') 
    args = parser.parse_args()
    
    logging.basicConfig(level=getattr(logging, args.loglevel))

    client = ExecutionBroker()
    client.run()
