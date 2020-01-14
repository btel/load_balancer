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

    if cmd == b'EOF':
        print("received EOF finishing work.")
        break

    # Do the work
    print('processing command %s' % cmd)
    process = subprocess.Popen(cmd, shell=True)

    while process.poll() is None:
        time.sleep(HEARTBEAT_INTERVAL)
        receiver.send_multipart([b'', b'ALIVE'])
