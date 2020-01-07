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

    def run(self):
        workers = self._workers
        queue = self.queue
        sender = self.sender

        while queue:
            address, _, msg = sender.recv_multipart()

            current_time = time.time()
            if msg == b'READY':
                # Random workload from 1 to 100 msecs
                payload = queue.pop()

                sender.send_multipart([address, b'', payload])
                workers[address] = {'payload': payload, 'last_seen': current_time}
                print("Sending payload:", payload)

            elif msg == b'ALIVE':
                if address in workers:
                    workers[address]['last_seen'] = current_time

            for addr in list(workers):
                worker_info = workers[addr]
                if worker_info['last_seen'] + TIMEOUT < current_time:
                    print("worker dead, need to restart with payload: %s", worker_info['payload'])
                    workers.pop(addr)
                    queue.append(worker_info['payload'])


if __name__ == '__main__':

    delays = range(100) #[random.randint(1, 100) for i in range(100)]
    cmds = [('sleep %.3f' % (d / 1000)) for d in delays]

    client = ExecutionClient(cmds)
    client.run()
