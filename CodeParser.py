#!/usr/bin/python3
#
# CodeParser.py: Object to parse Dalvik bytecode
#
# For documentation on Dalvik bytecode, see:
# https://source.android.com/devices/tech/dalvik/dalvik-bytecode.html
# https://source.android.com/devices/tech/dalvik/instruction-formats.html
#

from message import *
import struct

# Object for parsing Dalvik bytecode
class CodeParser:

    def __init__(self, bytecode, dex_version):

        self.dex_version = dex_version
        self.bytecode = bytecode
        self.insns = struct.unpack('H'*(len(self.bytecode)//2), self.bytecode)

    def __repr__(self):

        return str(self.insns)


if __name__ == '__main__':

    import sys
    import settings

    settings.VERBOSE = True
    settings.DEBUG = True

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <Code file>' % (sys.argv[0]), fatal=True, pre='usage')

    code_file = sys.argv[1]
    code = CodeParser(dex_file)

