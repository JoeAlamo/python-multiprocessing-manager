# python-multiprocessing-manager
Example of a Python multiprocessing implementation to manage worker processes, allowing for graceful shutdowns

Consists of 3 classes:

### Manager ###

This class creates and initialises a set number of workers and monitors them in a loop, automatically replacing them if a worker dies.

It also allows for a graceful exit of itself and all of it's workers by intercepting certain exit signals. 

It will wait for the workers to finish processing their current task before telling them to safely shutdown using inter-process Pipes for communication.

### WorkerProcess ###

The WorkerProcess class extends the base multiprocessing.Process class to attach the inter-process Pipe to the object for easy communication.

### Worker ###

The Worker class is responsible for the individual units of work that each worker process performs. 

It is set to work in a loop, and at the end of each task it will see if the Manager has instructed it to shut down safely, and will shut down if so.

## Use cases ##

The use case this prototype was developed for is RabbitMQ queue consumers. 

The Manager can be used to run multiple queue consumers in parallel for improved performance, resource utilisation and easier management.

The graceful exit feature also allows for updates to be safely applied to the fleet of queue consumers.
