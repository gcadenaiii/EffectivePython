""" Consider concurrent.futures for True Parallelism """

""" The multiprocess built-in module enables Python to utilize multiple CPU
cores in parallel by running additional interpreters as child processes.  
These child processes are separate from the main interpreter, so their global
interpreter locks are also separate.  Each child can fully utilize one CPU
core.  Each child has a link to the main process where it receives instructions
to do computation and returns results.
"""

from time import time
from concurrent.futures import ThreadPoolExecutor

def gcd(pair):
    a, b = pair
    low = min(a, b)
    for i in range(low, 0, -1):
        if a % i == 0 and b % i == 0:
            return i

# run in serial

numbers = [(1963309, 2265973), (2030677, 3814172),
           (1551645, 2229620), (2039045, 2020802)]

start = time()
results = list(map(gcd, numbers))
end = time()
print('Took %.3f seconds' % (end - start))

# the max_workers should match the number of CPU cores

start = time()
pool = ThreadPoolExecutor(max_workers=4)
result = list(pool.map(gcd, numbers))
end = time()
print('Took %.3f seconds' % (end - start))

