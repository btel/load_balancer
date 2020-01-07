import zmq
import random
import time

raw_input = input

TIMEOUT = 10
context = zmq.Context()

# Socket to send messages on
sender = context.socket(zmq.ROUTER)
sender.bind("tcp://*:5557")


print("Press Enter when the workers are ready: ")
_ = raw_input()
print("Sending tasks to workers…")

# Initialize random number generator
random.seed()

workers = {}
# Send 100 tasks
total_msec = 0
delays = range(100) #[random.randint(1, 100) for i in range(100)]
queue = [('sleep %.3f' % (d / 1000)).encode('ascii') for d in delays]

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

# Give 0MQ time to deliver
time.sleep(1)
