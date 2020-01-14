import sys
import time
import zmq
import subprocess

context = zmq.Context()


class Client:

    def __init__(self):
        # Socket to receive messages on
        self.receiver = context.socket(zmq.DEALER)
        self.receiver.connect("tcp://localhost:5558")

    def submit_jobs(self, jobs):
        for j in jobs:
            self.receiver.send_multipart([b'', j.encode('ascii')])

if __name__ == '__main__':

    client = Client()
    client.submit_jobs([" ".join(sys.argv[1:])])
