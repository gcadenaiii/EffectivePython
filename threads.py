""" Use Threads for Blocking I/O, Avoid for Parallelism """

"""
CPython runs a Python program in two steps.  First it parses and compiles the
source text into bytecode.  Then, it runs the butecode using a stack-based 
interpreter.  

Python enforces coherence with a mechanism called the global interpreter lock
(GIL).

Essentiall, the GIL is a mutual-exclusion lock (mutex) that prevents CPython
from being affected by preemptive multithreading.

The GIL has an important negative side effect.   The GIL causes only one
thread to make forward progress at a time.



"""
from time import time
from threading import Thread

def factorize(number):
    for i in range(1, number + 1):
        if number % i == 0:
            yield i

def old_factorize(number):
    factors = []
    for i in range(1, number +1):
        if number % i == 0:
            factors.append(number)
    return factors

numbers = [2139079, 1214759, 1516637, 1852285]

start = time()
for number in numbers:
    list(factorize(number))
end = time()
print('Took %.3f seconds' % (end - start))

"""
print('Traditional implementation')
start = time()
for number in numbers:
    old_factorize(number)
end = time()
print('Took %.3f seconds' % (end - start))
"""

class FactorizeThread(Thread):
    def __init__(self, number):
        super().__init__()
        self.number = number

    def run(self):
        self.factors = list(factorize(self.number))

start = time()
threads = []
for number in numbers:
    thread = FactorizeThread(number)
    thread.start()
    threads.append(thread)
for thread in threads:
    thread.join()
end = time()
print('Took %.3f seconds' % (end - start))

# It takes even longer than in serial, because of the effect of the GIL

"""
Reasons Python supports threading even though it has the GIL:
    1. multiple threads make it easy for your program to seem like it's doing
    multiple things at the same time.
    2. to deal with blocking I/O.  Threads help you handle blocking I/O by
    insulating your program from the time it takes for the operating system
    to respond to your requests.
"""

import select, socket

def slow_systemcall():
    select.select([socket.socket()], [], [], 0.1)

start = time()
for _ in range(5):
    slow_systemcall()
end = time()
print('Took %.9f seconds' % (end - start))

# but that was blocking and nothing else could progress

start = time()
threads = []
for _ in range(5):
    thread = Thread(target=slow_systemcall)
    thread.start()
    threads.append(thread)

def compute_helicopter_location(i):
    pass
    #print(i)

for i in range(5):
    compute_helicopter_location(i)

for thread in threads:
    thread.join()
end = time()
print('Took %.9f seconds' % (end - start))































