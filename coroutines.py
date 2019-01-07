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
    while True:
        value = yield current       # return current value 
        current = min(value, current)

it = minimize()         # established the function as an iterator
next(it)                # prime the generator
print(it.send(10))
print(it.send(4))
print(it.send(22))
print(it.send(-1))

""" Like threads, coroutines are independent functions that can consume
inputs from their environment and produce resulting outputs.  The difference
is that coroutines pause at each yield expression in the generator function
and resume after each call to send from the outside.

This is the magical mechanism of Coroutines.  

This behaviour allows the code consuming the gerneator to take action after
each yield expression in the coroutine, e.g., use the generator's output 
values to call other functions and update data structures.

MOST IMPORTANTLY, it can advance other generator functions until their next
yield expressions.  By advancing many separate generators in lockstep, they
will all seem to be running simultaneously, mimicking the concurrent behaviour
of Python threads.

"""

# Game of Life

"""
Use Coroutines to implement Conway's Game of Life.  The rules:  You have a 2D
grid of arbritrary size. Each cell can either be alive or empty.

ALIVE = '*'
EMPTY = '-'

The game progresses one tick of the clock at a time.  At each tick, each cell
counts how many of its neighboring eight cells are still alive.  Based on its
neighbor count, each cell decides if it will keep living, die, or regenerate.
"""

# Model this game by representing each cel as a generator coroutine running
# in lockstep with all of the others.

# Step 1. Need a way to retrieve the status of neighboring cells
# do this with a coroutine named count_neighbors that works by yielding Query
# objects

# provide the generator coroutine with a way to ask its surrounding env for 
# information

from collections import namedtuple

ALIVE = '*'
EMPTY = '-'
Query = namedtuple('Query', ('y', 'x'))

# the result of each yield will be an ALIVE or EMPTY

def count_neighbors(y, x):
    n_ = yield Query(y + 1, x + 0)      # North
    ne = yield Query(y + 1, x + 1)      # Northeast
    e_ = yield Query(y + 0, x + 1)      # East
    se = yield Query(y - 1, x + 1)      # Southeast
    s_ = yield Query(y - 1, x + 0)      # Southeast
    sw = yield Query(y - 1, x - 1)      # Southwest
    w_ = yield Query(y + 0, x - 1)      # West
    nw = yield Query(y + 1, x - 1)      # Northwest

    neighbor_states = [n_, ne, e_, se, s_, sw, w_, nw]
    count = 0
    for state in neighbor_states:
        if state == ALIVE:
            count += 1
    return count

# drive the coroutine with fake data to test it

it = count_neighbors(10, 5)
q1 = next(it)                   # Get the first Query
print('First   yield:', q1)
q2 = it.send(ALIVE)             # Send q1 state, get q2
print('Second  yield:', q2)
q3 = it.send(ALIVE)             # Send q2 state, get q3
print('Third   yield:', q3)
q4 = it.send(EMPTY)             # Send q3 state, get q4
print('Fourth  yield:', q4)
q5 = it.send(EMPTY)             # Send q4 state, get q5
print('Fifth   yield:', q5)
q6 = it.send(EMPTY)             # Send q5 state, get q6
print('Sixth   yield:', q6)
q7 = it.send(EMPTY)             # Send q6 state, get q7
print('Seventh yield:', q7)
q8 = it.send(EMPTY)             # Send q7 state, get q8
print('Eighth  yield:', q8)

try:
    it.send(EMPTY)              # Send q8 state, retrieve count
except StopIteration as e:
    print('Count: ', e.value)   # Value from return statement

""" Now I need the ability to indicate that a cell will transition to a new
state in response to the neighbor count.  Do this with another coroutine 
called step_cell.  This generator will indicate transitions in a cell's state
by yielding Transition objects.
"""

Transition = namedtuple('Transition', ('y', 'x', 'state'))

def game_logic(state, neighbors):
    if state == ALIVE:
        if neighbors < 2:
            return EMPTY        # Die: Too few
        elif neighbors > 3:
            return EMPTY        # Die: Too Many
    else:
        if neighbors == 3:
            return ALIVE        # Regenerate
    return state


def step_cell(y, x):
    state = yield Query(y, x)
    neighbors = yield from count_neighbors(y, x)
    next_state = game_logic(state, neighbors)
    yield Transition(y, x, next_state)

""" the call to count_neighbors uses the yield from expression.
This expression allows Python to compose generator coroutines together,
making it easy to reuse smaller pieces of functionality to build complex
coroutines from simpler ones.  

When count_neighbors is exhausted, the final value it returns (with the return
statement) will be passed to step_cell as the result of the yield from 
expression.
"""

# drive the coroutine with fake data to test it

it = step_cell(10, 5)
q0 = next(it)                   # Initial location query
print('Me:           ', q0)
q1 = it.send(ALIVE)             # send my status, get neighbor query
print('Q1:           ', q1)
q2 = it.send(ALIVE)             #
print('Q2:           ', q2)
q3 = it.send(EMPTY)             #
print('Q3:           ', q3)
q4 = it.send(EMPTY)             #
print('Q4:           ', q4)
q5 = it.send(EMPTY)             #
print('Q5:           ', q5)
q6 = it.send(EMPTY)             #
print('Q6:           ', q6)
q7 = it.send(EMPTY)             #
print('Q7:           ', q7)
q8 = it.send(EMPTY)             #
print('Q8:           ', q8)

t1 = it.send(EMPTY)             # Send for q8, get game decision
print('Outcome:      ', t1)


""" Now to run this logic for a whole grid of cells in lockstep.  
Simulate coroutine progresses the grid of cells forward by yielding from
step_cell many times.  After processing every coordinate, it yields a TICK 
object to indicate that the current generation of cells have all 
transitioned.
"""

TICK = object()

def simulate(height, width):
    while True:
        for y in range(height):
            for x in range(width):
                yield from step_cell(y, x)
        yield TICK

class Grid(object):
    def __init__(self, height, width):
        self.height = height
        self.width = width
        self.rows = []
        for _ in range(self.height):
            self.rows.append([EMPTY] * self.width)

    def __str__(self):
        return 'grid...'

    def query(self, y, x):
        return self.rows[y % self.height][x % self.width]

    def assign(self, y, x, state):
        self.rows[y % self.height][x % self.width] = state


def live_a_generation(grid, sim):
    progeny = Grid(grid.height, grid.width)
    item = next(sim)
    while item is not TICK:
        if isinstance(item, Query):
            state = grid.query(item.y, item.x)
            item = sim.send(state)
        else:       # Must be a Tansition
            progeny.assign(item.y, item.x, item.state)
            item = next(sim)
    return progeny

class ColumnPrinter(object):
    pass


grid = Grid(5, 9)
grid.assign(0, 3, ALIVE)
#print(grid)

columns = ColumnPrinter()
sim = simulate(grid.height, grid.width)
for i in range(5):
    columns.append(str(grid))
    grid = live_a_generation(grid, sim)


print(columns)























