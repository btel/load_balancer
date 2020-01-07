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
    cmd = receiver.recv()

    # Simple progress indicator for the viewer
    sys.stdout.write('.')
    sys.stdout.flush()

    # Do the work
    process = subprocess.Popen(cmd, shell=True)

    while process.poll() is None:
        receiver.send_multipart([b'', b'ALIVE'])
        time.sleep(HEARTBEAT_INTERVAL)
