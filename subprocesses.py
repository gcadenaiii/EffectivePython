""" Use subprocess to Manage Chile Processes """

# The best and simplest choice for managing child processes is to use the 
# subprocess built-in module
import subprocess
import os
from time import time

# Popen constructor starts the process
# communicate method resads the child processes's output AND waits for 
# termination
proc = subprocess.Popen(
        ['echo', 'Hello from the child!'],
        stdout=subprocess.PIPE)
out, err = proc.communicate()
print(out.decode('utf-8'))

# the status of child processes can be polled periodically while Python does
# other work

proc = subprocess.Popen(['sleep', '0.000001'])
while proc.poll() is None:
    print('Working...')

print('Exit status', proc.poll())

# Enable parallel processing by starting all of the child processes up front
def run_sleep(period):
    proc = subprocess.Popen(['sleep', str(period)])
    return proc

start = time()
procs = []
for i in range(10):
    proc = run_sleep(0.2)
    print('started thread %i' % i)
    procs.append(proc)
# Wait for them to finish their I/O and terminate with communicate
for proc in procs:
    proc.communicate()
end = time()
print('Finished in %.3f seconds' % (end - start))

# Pipe the data from your Python program into a subprocess and retrieve its
# output

# use the openssl command-line tool to encrypt some data
def run_openssl(data):
    env = os.environ.copy()
    env['password'] = b'\xe24U\nxd0Q13S\x11'
    proc = subprocess.Popen(
            ['openssl', 'enc', '-des3', '-pass', 'env:password'],
            env=env,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE)
    proc.stdin.write(data)
    proc.stdin.flush()  #Ensure the child gets input
    return proc

# pipe random bytes into the encryption function

procs = []
for _ in range(3):
    data = os.urandom(10)
    proc = run_openssl(data)
    procs.append(proc)

for proc in procs:
    out, err = proc.communicate()
    print(out[-10:])

# create chains of // processes, i.e. connecting the output of one child
# process to the input of another

def run_md5(input_stdin):
    proc = subprocess.Popen(
            ['md5sum'],
            stdin=input_stdin,
            stdout=subprocess.PIPE)
    return proc

# openssl processes to encrypt some data
# another set of processes to md5 hash the encrypted output

input_procs = []
hash_procs = []

for _ in range(3):
    data = os.urandom(10)
    proc = run_openssl(data)
    input_procs.append(proc)
    hash_proc = run_md5(proc.stdout)
    hash_procs.append(hash_proc)

# wait for the processes to finish

for proc in input_procs:
    proc.communicate()
for proc in hash_procs:
    out, err = proc.communicate()
    print(out.strip())

# if one the child processes hangs, pass the timeout flag to the communicate
# method.  This will cause an exception to be raised if the process hasn't
# responded within the time period

proc = run_sleep(3)
try:
    proc.communicate(timeout=0.1)
except subprocess.TimeoutExpired:
    proc.terminate()
    proc.wait()

print('Exit status', proc.poll())



































