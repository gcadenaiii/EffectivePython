""" Use Lock to Prevent Data Races in Threads """

from threading import Thread
from threading import Lock
from time import time

class Counter(object):
    def __init__(self):
        self.count = 0

    def increment(self, offset):
        self.count += offset


def worker(sensor_index, how_many, counter):
    for _ in range(how_many):
        counter.increment(1)

def run_threads(func, how_many, counter):
    threads = []
    for i in range(5):
        args = (i, how_many, counter)
        thread = Thread(target=func, args=args)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

how_many = 10**5
counter = Counter()
start = time()
run_threads(worker, how_many, counter)
end = time()
unlocked = end - start
print('Counter should be %d, found %d' %
        (5 * how_many, counter.count))
print('Took %.3f seconds' % unlocked)

# the result is way off.  You don't know exactly when Python will suspend
# threads and will resume another thread in turn.
# the Lock class from the threading module is the simplest and most useful.  
# it is a mutual exclusion lock (mutex)

# use a with statement to acquire and release the lock.  It makes it easier 
# to see which code is exdecuting while the lock is help

class LockingCounter(object):
    def __init__(self):
        self.lock = Lock()
        self.count = 0

    def increment(self, offset):
        with self.lock:
            self.count += offset

counter = LockingCounter()
start = time()
run_threads(worker, how_many, counter)
end = time()
locked = end - start
print('Counter should be %d, found %d' %
        (5 * how_many, counter.count))
print('Took %.3f seconds' % locked)

print('%.2fx Increase' % (locked / unlocked))

























