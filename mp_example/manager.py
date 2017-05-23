import multiprocessing
import signal
import sys
import time
from collections import OrderedDict
from mp_example.worker_process import WorkerProcess


class ConsumerManager(object):

    # Whether it is currently running
    running = False
    # Target function for workers to execute
    target = None
    # The exit signals we shall trap (SIGKILL can't be caught)
    exit_signals = ['SIGHUP', 'SIGINT', 'SIGQUIT', 'SIGTERM']
    # Dict of WorkerProcess instances
    workers = OrderedDict()
    # Number of workers to run
    worker_count = 0

    def __init__(self, worker_count, target):
        self.worker_count = worker_count
        self.target = target

    """Run the workers. Should only be called once"""
    def run(self):
        if self.running:
            return

        # Create and start the workers
        self._initialise_workers()

        self.running = True

        # Main loop
        while True:
            for k, worker in self.workers.iteritems():
                # is_alive checks if the process is alive and active
                if not worker.is_alive():
                    print("{} is not alive".format(worker.name))
                    # Join to remove possible zombie process
                    worker.join(10)
                    # Create new worker and replace original
                    self._start_worker(k)

            time.sleep(10)

    """Exit gracefully, shutting the workers down safely one by one"""
    def graceful_exit(self):
        for k, worker in self.workers.iteritems():
            print("Sending poison pill to {}".format(worker.name))
            worker.parent_conn.send("die")

        for k, worker in self.workers.iteritems():
            # Wait 10 seconds for the child process to merge back into the parent
            worker.join(10)
            if worker.is_alive():
                print("{} is still alive, forcefully terminating".format(worker.name))
                worker.terminate()
                worker.join(5)

        sys.exit(0)

    """Handler for exit signals, initiate graceful exit"""
    def _exit_signal_handler(self, signum, frame):
        print("Signal {} received, exiting gracefully".format(signum))
        self.graceful_exit()

    """Set the process' handler for exit signals. This is inherited by worker processes
    created by the manager. Before creating a worker, we set the exit signal handler to
    SIG_IGN, which ignores exit signals. We then change it to our custom handler.
    This allows the manager to handle exit signals on behalf of the workers, and shut
    them all down gracefully."""
    def _set_exit_signal_handler(self, handler):
        # Get all signals in the signal module
        for sig_name in [x for x in dir(signal) if x.startswith('SIG')]:
            # If it is an exit signal, set the handler
            if sig_name in self.exit_signals:
                signum = getattr(signal, sig_name)
                signal.signal(signum, handler)

    """Set up the workers"""
    def _initialise_workers(self):
        if self.running:
            return

        for k in xrange(1, self.worker_count + 1):
            self._start_worker(k)

    """Start the worker process, adding it to our pool of workers"""
    def _start_worker(self, key):
        # Make worker ignore exit signals
        self._set_exit_signal_handler(signal.SIG_IGN)

        worker_name = "worker-{}".format(key)
        print("Starting {}".format(worker_name))
        # Create duplex pipe between parent and worker for inter process communication
        parent_conn, child_conn = multiprocessing.Pipe(True)
        p = WorkerProcess(name=worker_name, target=self.target, parent_conn=parent_conn, args=(child_conn,))
        self.workers[key] = p
        p.start()

        # Restore exit signal handling
        self._set_exit_signal_handler(self._exit_signal_handler)
