""" part 2 of queue """

"""
When the worker functions vary in speeds an earlier phase can prevent
progress in later phases, backing up the pipeline.  

The outcome is that worker threads waste CPU time doing nothing useful (they 
are constantly raising and catching exceptions)

There are three problems with this implementation:
1. Determining whether all of the work is complete requires yet another busy
wait on the done_queue.
2. In Worker, the run method will execute forever in its busy loop.  There is 
no way to signal to a worker thread that it is time to exit
3. A backup in the pipeline can cause the program to crash arbritrarily.

The lesson: It's hard to build a good producer-consumer queue yourself.

The Queue class from the queue module provides all of the functionality that 
you need.
1. Eliminates the busy waiting in the worker by making the get method block
until new data is available.
"""
from threading import Thread
from queue import Queue
import time

queue = Queue()

def consumer1():
    print('Consumer waiting')
    queue.get()
    print('Consumer done')

thread = Thread(target=consumer1)
thread.start()

print('Producer putting')
queue.put(object())
thread.join()
print('Producer done')

""" to solve the pipeline backup issue, the Queue class lets you specify the
maximum amount of pending work you'll allow between two phases.  This buffer
size calls to put to block when the queue is already full.
"""
queue = Queue(1)            # Buffer size of 1

def consumer2():
    time.sleep(0.1)         # Wait
    queue.get()             # Runs second
    print('Consumer got 1')
    queue.get()             # Runs fourth
    print('Consumer got 2')

thread = Thread(target=consumer2)
thread.start()

# the wait should allow the producer thread to put both objects on the Queue
# before the consumer thread ever calls get.

# NOTE: Since the buffer size is 1.  The Producer will have to wait until the
# consumer thread calls get at least once.  Queue enforces blocking to prevent
# the Queue from overflowing past it's buffer size.

queue.put(object())         # runs first
print('Producer put 1')
queue.put(object())         # runs third
print('Producer put 2')
thread.join()
print('Producer done')

# The Queue class can also track the progress of work using the task_done
# method.  This lets you wait for a phase's input queue to drain and
# eliminates the need for polling the done_queue at the end of your pipeline.

in_queue = Queue()

def consumer3():
    print('Consumer waiting')
    work = in_queue.get()           # Done second
    print('Consumer working')
    # Doing work...
    print('Consumer done')
    in_queue.task_done()            # Done third

thread = Thread(target=consumer3)
thread.start()

in_queue.put(object())              # Done first
print('Producer waiting')
in_queue.join()                     # Done fourth
print('Producer done')

# NOTE: Now, the prducer code doesn't have to join the consumer3 thread or
# poll.  The producer can just wait for the in_queue to finish by calling join
# on the Queue instance.  Even once its empty, the in_queue won't be joinable
# until after task_done is called for every item that was ever enqueued.

""" Put this together into a Queue subclass that also tells the Worker thread
when it should stop processing.
"""

class ClosableQueue(Queue):
    SENTINEL = object()

    def close(self):
        self.put(self.SENTINEL)

    # define an iterator for the queue that looks for this special object
    def __iter__(self):
        while True:
            item = self.get()
            try:
                if item is self.SENTINEL:
                    return      # Cause thread to exit
                yield item
            finally:
                self.task_done()

""" Now redifine worker to rely on the behavior of the ClosableQueue class.
"""

class StoppableWorker(Thread):
    def __init__(self, func, in_queue, out_queue):
        super().__init__
        self.func = func
        self.in_queue = in_queue
        self.out_queue = out_queue

    def run(self):
        for item in self.in_queue:
            result = self.func(item)
            self.out_queue.put(result)

""" Recreate the worker threads using the new worker class """
download_queue = ClosableQueue()
resize_queue = ClosableQueue()
upload_queue = ClosableQueue()
done_queue = ClosableQueue()

threads = [
    StoppableWorker(download, download_queue, resize_queue),
    StoppableWorker(resize, resize_queue, upload_queue),
    StoppableWorker(upload, upload_queue, done_queue)
]

""" Now I can put a stop signal once all of the input work has been injected
"""
for thread in threads:
    thread.start()
for _ in range(1000):
    download_queue.put(object())
download_queue.close()      # close signal

""" Now I can wait for the work to finish by joining each queue that connects
the phases.  Each time one phase is done, I signal the next phase to stop by
closing the input queue.
"""

download_queue.join()
resize_queue.close()
resize_queue.join()
upload_queue.close()
upload_queue.join()
print(done_queue.qsize(), 'items finished')

"""
NOTE: Whenyou call queue.join() in the main thread, all it does is block the
main threads until the workers have processed everything that's in that queue.
It does not stop the worker threads, which continue executing their inf. loops.
"""























