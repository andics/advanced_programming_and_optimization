# Import packages. You can import additional packages, if you want
# You can change the way they are imported, e.g import pulp as pl or whatever
# But take care to adapt the solver configuration accordingly.
from pulp import *
import matplotlib.pyplot as plt

# Use the following solver
solver = COIN_CMD(path="/usr/bin/cbc",threads=8)
# at home, you can try it with different solvers, e.g. GLPK, or with a different
# number of threads.
# WARNING: your code when run in vocareum should finish within 10 minutes!!!

def bakery():
    # Input file is called ./bakery.txt
    input_filename = './bakery.txt'

    # Use solver defined above as a parameter of .solve() method.
    # e.g., if your LpProblem is called prob, then run
    # prob.solve(solver) to solve it.


    # Write visualization to the correct file:
    visualization_filename = './visualization.png'

    # retval should be a dictionary such that retval['s_i'] is the starting
    # time of pastry i
    return retval
