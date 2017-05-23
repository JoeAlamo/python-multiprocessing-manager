import os
import random
import sys
import time


class Worker(object):

    def __init__(self, child_conn):
        self.child_conn = child_conn

    """Main work loop for worker - does nothing, only demonstration purposes"""
    def work(self):
        while True:
            print("Worker process {} working".format(os.getpid()))
            # 20% chance of randomly exiting to demonstrate that manager will create new worker in place
            if random.Random().randint(1, 100) > 80:
                print("Worker process {} randomly exiting".format(os.getpid()))
                sys.exit(0)
            else:
                time.sleep(10)

            # Has manager sent us anything?
            if self.child_conn.poll(2):
                # If so, read the message
                message = self.child_conn.recv()
                # If it's telling us to die, kill ourselves :-)
                if message == "die":
                    print("Worker process {} exiting".format(os.getpid()))
                    sys.exit(0)


def create_worker(child_conn):
    """This is the target function that managers use to create a Worker"""
    worker = Worker(child_conn)
    worker.work()
