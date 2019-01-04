""" Consider Coroutines to Run Many Functions Concurrently """

""" Threads require a lot of memory, about 8 MB per executing thread.  Threads
are costly to start.   Python can work around these issues with coroutines.
Coroutines let you have many seeminly simultaneous function in your Python
programs.  They are implemented as an extension to generators.  AND the cost
of starting a generator coroutine is a function call, once active they use
less than 1 KB of memory.

Coroutines work by enabling the code consuming a generator to send a value
back into the generator function after each yield expression.
"""

def my_coroutine():
    while True:
        received = yield
        print('Recieved:', received)

it = my_coroutine()
next(it)        # Prime the coroutine
it.send('First')
it.send('Second')

""" The initial call to next is required to prepare the generator for
receiving the first send by advancing it to the first yield expression.
Together, yield and send provide generators with a standard way to vary the
next yielded value in response to external input.
"""

# implement a generator corouting that yields the minimum value it's been
# sent so far

def minimize():
    current = yield
    while True
