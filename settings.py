#!/usr/bin/python3
#
# settings.py: project-wide settings file
#

# `x in NO_FILTER` will always return True
class NO_FILTER:
    __contains__ = lambda self, item: True

VERBOSE = False             # Whether output is verbose
DEBUG = False               # Whether to display debug output
DEBUG_FILTER = NO_FILTER()  # 'who' filters for debugging

