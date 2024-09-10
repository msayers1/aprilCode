import os
from profile import run
from pstats import Stats

code = open('pyb.py', 'r').read()

filename = 'profile-data.txt'
run(code, filename)

s = Stats(filename)
s.strip_dirs().sort_stats(-1).print_stats()

os.remove(filename)
