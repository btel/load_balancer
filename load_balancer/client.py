import zmq
import random
import time

raw_input = input

TIMEOUT = 10
context = zmq.Context()


class ExecutionClient:

    def __init__(self, commands):
        """commands - shell commands to execute."""

        # Socket to send messages on
        self.sender = context.socket(zmq.ROUTER)
        self.sender.bind("tcp://*:5557")
        self.queue = [c.encode('utf8') for c in commands]
        self._workers = {}

    def _event_loop(self):

        workers = self._workers
        queue = self.queue
        sender = self.sender

        while queue or workers:
            address, _, msg = sender.recv_multipart()

            current_time = time.time()
            if msg == b'READY':
                workers.pop(address, None)
                

                if not queue:
                    # use dummy job to keep the worker waiting for new tasks
                    payload = b''
                    workers.pop(address, None)
                else:
                    payload = queue.pop()
                    workers[address] = {'payload': payload, 'last_seen': current_time}

                sender.send_multipart([address, b'', payload])
                print("Sending payload:", payload)

            elif msg == b'ALIVE':
                if address in workers:
                    workers[address]['last_seen'] = current_time

            self._check_alive()


    def _check_alive(self):
        workers = self._workers
        queue = self.queue

        current_time = time.time()

        for addr in list(workers):
            worker_info = workers[addr]
            if worker_info['last_seen'] + TIMEOUT < current_time:
                print("worker dead, need to restart with payload: %s", worker_info['payload'])
                workers.pop(addr)
                queue.append(worker_info['payload'])

    def _wait_for_jobs(self):

        workers = self._workers
        queue = self.queue
        sender = self.sender

        while workers:
            address, _, msg = sender.recv_multipart()

            if msg == b'READY':
                workers.pop(address, None)

                # need to send an empty job to keep the worker waiting for incoming tasks
                sender.send_multipart([address, b'', b''])

            elif msg == b'ALIVE':
                if address in workers:
                    current_time = time.time()
                    workers[address]['last_seen'] = current_time


    def run(self):

        # run main event loop
        self._event_loop()

        # wait for all jobs to finish
        #self._wait_for_jobs()

if __name__ == '__main__':

    delays = list(range(5)) #[random.randint(1, 100) for i in range(100)]
    delays[0] = 20000
    cmds = [('sleep %.3f' % (1 + d / 1000)) for d in delays]

    client = ExecutionClient(cmds)
    client.run()
