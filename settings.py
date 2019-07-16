#!/usr/bin/python3
#
# settings.py: project-wide settings file
#

import sys

# `x in NO_FILTER` will always return True
class NO_FILTER:
    __contains__ = lambda self, item: True

DEBUG = False               # Whether to display debug output
DEBUG_FILTER = NO_FILTER()  # 'who' filters for debugging
TRAIN_PERCENTAGE = 0.4      # Percentage for training set
NAME = sys.argv[0]          # Executable name
N_THREADS = 17              # Number of execution threads
VERBOSE = False             # Whether output is verbose
PARALLEL = True             # Whether to multithread

