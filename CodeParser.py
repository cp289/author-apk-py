#!/usr/bin/python3
#
# CodeParser.py: Object to parse Dalvik bytecode
#
# For documentation on Dalvik bytecode, see:
# https://source.android.com/devices/tech/dalvik/dalvik-bytecode.html
# https://source.android.com/devices/tech/dalvik/instruction-formats.html
#

import CodeFormat
import math
from message import *
import settings
import struct

# General class for parsing instructions
class Instruction:
    format = 'Instruction'
    format_args = ()
    def __repr__(self):
        return 'Instruction' % self.format_args

# Object for parsing Dalvik bytecode
class CodeParser:

    def __init__(self, bytecode, dex_version):
        self.dex_version = dex_version
        # Convert bytecode to large int
        self.intcode = int.from_bytes(bytecode, byteorder='little')
        self.insns = []

        i = 0
        while i < self.intcode.bit_length():
            ins = CodeFormat.Instruction(self.intcode, i)
            if ins.name == 'UNUSED':
                error('    ', 'Previous instruction: %s' %
                        (format(self.insns[-1])))
                error('    ', 'Code section bit size: %s' %
                        (hex(self.intcode.bit_length())))
            self.insns.append(ins)

            ilen = ins.idx - i
            if ilen & 0xf != 0:
                error('CodeParser', 'bad instruction length: %s' % (hex(ilen)))
                error('CodeParser', 'bad instruction: %s' % (format(ins)))

            i = ins.idx

    def __repr__(self):
        return str(self.insns)

if __name__ == '__main__':

    import sys

    settings.VERBOSE = True
    settings.DEBUG = True
    #settings.DEBUG_FILTER = ('CodeParser',)

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <Code file>' % (sys.argv[0]), fatal=True, pre='usage')

    with open(sys.argv[1], 'rb') as code_file:
        bytecode = code_file.read()

    code = CodeParser(bytecode, 39)

