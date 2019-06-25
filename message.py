#!/usr/bin/python3
#
# message.py: library for printing error, warning, and verbose messages
#

import settings
import sys


# Output an error message and exit if necessary
def error(who, msg, fatal=False, exit_code=-1, pre='error'):

    print('%s: %s: %s' % (who, pre, msg), file=sys.stderr)
    if fatal: exit(exit_code)


# Print a warning message
def warn(who, msg):

    error(who, msg, pre='warning')


# Print verbose output
def verb(who, msg):

    if settings.VERBOSE: print('%s: %s' % (who, msg))


# Print debug message
def debug(who, msg):

    if settings.DEBUG: print('%s: %s' % (who, msg), file=sys.stderr)

