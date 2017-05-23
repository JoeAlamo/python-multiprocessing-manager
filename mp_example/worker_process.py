import multiprocessing


class WorkerProcess(multiprocessing.Process):

    """Override init to attach parent_conn pipe as class member for manager to communicate with worker"""
    def __init__(self, parent_conn, group=None, target=None, name=None, args=(), kwargs={}):
        super(WorkerProcess, self).__init__(
            group=group,
            target=target,
            name=name,
            args=args,
            kwargs=kwargs
        )

        self.parent_conn = parent_conn
