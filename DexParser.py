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
        self.checksum, = struct.unpack('I', dex_file.read(4))
        self.signature = struct.unpack('BBBBBBBBBBBBBBBBBBBB',
             dex_file.read(20))

        # TODO would changing this to a single unpack command be faster?
        # TODO Approach: unpack everything at once and create an iterator to
        # assign to object fields
        self.file_size, = struct.unpack('I', dex_file.read(4))
        self.size, = struct.unpack('I', dex_file.read(4))
        self.endian_tag, = struct.unpack('I', dex_file.read(4))
        self.link_size, = struct.unpack('I', dex_file.read(4))
        self.link_off, = struct.unpack('I', dex_file.read(4))
        self.map_off, = struct.unpack('I', dex_file.read(4))
        self.string_ids_size, = struct.unpack('I', dex_file.read(4))
        self.string_ids_off, = struct.unpack('I', dex_file.read(4))
        self.type_ids_size, = struct.unpack('I', dex_file.read(4))
        self.type_ids_off, = struct.unpack('I', dex_file.read(4))
        self.proto_ids_size, = struct.unpack('I', dex_file.read(4))
        self.proto_ids_off, = struct.unpack('I', dex_file.read(4))
        self.field_ids_size, = struct.unpack('I', dex_file.read(4))
        self.field_ids_off, = struct.unpack('I', dex_file.read(4))
        self.method_ids_size, = struct.unpack('I', dex_file.read(4))
        self.class_defs_size, = struct.unpack('I', dex_file.read(4))
        self.class_defs_off, = struct.unpack('I', dex_file.read(4))
        self.data_size, = struct.unpack('I', dex_file.read(4))
        self.data_off, = struct.unpack('I', dex_file.read(4))


class DexMapItem:

    # Type id definitions
    type = {
            0 : 'header_item',
            1 : 'string_id_item',
            2 : 'type_id_item',
            3 : 'proto_id_item',
            4 : 'field_id_item',
            5 : 'method_id_item',
            6 : 'class_def_item',
            7 : 'call_site_id_item',
            8 : 'method_handle_item',
            (1 << 12) : 'map_list',
            (1 << 12) + 1 : 'type_list',
            (1 << 12) + 2 : 'annotation_set_ref_list',
            (1 << 12) + 3 : 'annotation_set_item',
            (1 << 13) + 0 : 'class_data_item',
            (1 << 13) + 1 : 'code_item',
            (1 << 13) + 2 : 'string_data_item',
            (1 << 13) + 3 : 'debug_info_item',
            (1 << 13) + 4 : 'annotation_item',
            (1 << 13) + 5 : 'encoded_array_item',
            (1 << 13) + 6 : 'annotations_directory_item'
            }

    def __init__(self, byte_data):
        self.type, self.size, self.offset = struct.unpack('HxxII', byte_data)

    # Produce nice string formatting of object
    def __repr__(self):
        return '%s[%d] AT %s' % (DexMapItem.type[self.type], self.size,
                hex(self.offset))


class DexParser:

    def __init__(self, dex_file_path):
        self.FILE_PATH = dex_file_path

        with open(self.FILE_PATH, 'rb') as dex_file:
            self.header = DexHeader(dex_file)

            # Verify header magic and report DEX version
            if self.header.VALID:
                verb('DexParser', 'found DEX v.%d header for %s' %
                        (self.header.VERSION, self.FILE_PATH))
            else:
                error('DexParser', 'invalid DEX header magic for %s' %
                        (self.FILE_PATH))
                return

            # Check file endianness
            if self.header.endian_tag == int('0x78563412', 16):
                warn('DexParser', 'found reversed endian tag in %s' %
                        (dex_file_path))
                error('DexParser', 'reversed endian parsing not implemented',
                        fatal=True)
            elif self.header.endian_tag != int('0x12345678', 16):
                error('DexParser', 'found invalid endian tag for %s' %
                        (dex_file_path))

            self.readMap(dex_file)

        verb('DexParser\n', self.map)

    # Parse DEX file map
    def readMap(self, dex_file):

        dex_file.seek(self.header.map_off)              # Go to the file map
        size, = struct.unpack('I', dex_file.read(4))    # Parse # of elements in the DEX map

        # return array of DexMapItem objects
        self.map = [ DexMapItem(dex_file.read(12)) for i in range(size) ]
        return self.map


if __name__ == '__main__':

    import sys

    settings.VERBOSE = True

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <DEX file>' % (sys.argv[0]), fatal=True, pre='usage')

    dex_file = sys.argv[1]
    dex = DexParser(dex_file)

    print(dir(dex.header))

