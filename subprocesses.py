""" Use subprocess to Manage Child Processes """

# The best and simplest choice for managing child processes is to use The
# subprocess built-in module.

# the Popen constuctor starts the process 
# the Communicate method reads the child process's output and waits for
# termination
import subprocess

proc = subprocess.Popen(['sleep', '0.3'])
while proc.poll() is None:
    print ('Working...')














