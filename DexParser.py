#!/usr/bin/python3
#
# DexParser.py: Object to parse dex files
#
# For documentation on the DEX file format, see:
# https://source.android.com/devices/tech/dalvik/dex-format
#
# For documentation on the struct module, see:
# https://docs.python.org/3/library/struct.html
#

from message import *
import struct


# Dex file magic constants
DEX_MAGIC_PREFIX = tuple( [int(i, 16) for i in '0x64 0x65 0x78 0x0a'.split()] )


# Object for storing DEX file header
class DexHeader:

    def __init__(self, dex_file):

        self.VALID = True
        header_magic = struct.unpack('BBBBBBBB', dex_file.read(8))

        # Detect valid DEX header
        if header_magic[:4] != DEX_MAGIC_PREFIX or header_magic[7] != 0:
            self.VALID = False
            return

        self.VERSION = int(struct.pack('bbb', *header_magic[4:7]))

        self.magic = header_magic
        self.checksum = struct.unpack('I', dex_file.read(4))
        self.signature = struct.unpack('BBBBBBBBBBBBBBBBBBBB',
             dex_file.read(20))

        # TODO would changing this to a single unpack command be faster?
        self.file_size = struct.unpack('I', dex_file.read(4))
        self.size = struct.unpack('I', dex_file.read(4))
        self.endian_tag = struct.unpack('I', dex_file.read(4))
        self.link_size = struct.unpack('I', dex_file.read(4))
        self.link_off = struct.unpack('I', dex_file.read(4))
        self.map_off = struct.unpack('I', dex_file.read(4))
        self.string_ids_size = struct.unpack('I', dex_file.read(4))
        self.string_ids_off = struct.unpack('I', dex_file.read(4))
        self.type_ids_size = struct.unpack('I', dex_file.read(4))
        self.type_ids_off = struct.unpack('I', dex_file.read(4))
        self.proto_ids_size = struct.unpack('I', dex_file.read(4))
        self.proto_ids_off = struct.unpack('I', dex_file.read(4))
        self.field_ids_size = struct.unpack('I', dex_file.read(4))
        self.field_ids_off = struct.unpack('I', dex_file.read(4))
        self.method_ids_size = struct.unpack('I', dex_file.read(4))
        self.class_defs_size = struct.unpack('I', dex_file.read(4))
        self.class_defs_off = struct.unpack('I', dex_file.read(4))
        self.data_size = struct.unpack('I', dex_file.read(4))
        self.data_off = struct.unpack('I', dex_file.read(4))


class DexParser:

    def __init__(self, dex_file_path):
        self.FILE_PATH = dex_file_path

        with open(self.FILE_PATH, 'rb') as dex_file:
            self.header = DexHeader(dex_file)

            if self.header.VALID:
                verb('parse_dex', 'found DEX v.%d header for %s' %
                        (self.header.VERSION, self.FILE_PATH))
            else:
                error('parse_dex', 'invalid DEX header magic for %s' %
                        (self.FILE_PATH))


if __name__ == '__main__':

    import sys

    settings.VERBOSE = True

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <DEX file>' % (sys.argv[0]), fatal=True, pre='usage')

    dex_file = sys.argv[1]
    dex = DexParser(dex_file)

    print(dir(dex.header))

