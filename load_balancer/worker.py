import sys
import time
import zmq
import subprocess

context = zmq.Context()

# Socket to receive messages on
receiver = context.socket(zmq.DEALER)
receiver.connect("tcp://localhost:5557")

HEARTBEAT_INTERVAL = 1.

# Process tasks forever
while True:
    receiver.send_multipart([b'', b'READY'])
    _, cmd = receiver.recv_multipart()

    if not cmd:
        print("received empty command. Keep waiting for tasks")
        time.sleep(HEARTBEAT_INTERVAL)
        continue

    # Do the work
    print('processing command %s' % cmd)
    process = subprocess.Popen(cmd, shell=True)

    while process.poll() is None:
        time.sleep(HEARTBEAT_INTERVAL)
        receiver.send_multipart([b'', b'ALIVE'])
