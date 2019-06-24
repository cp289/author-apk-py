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
# For documentation on Modified UTF-8 encoding (MUTF-8), see:
# ?
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


# Dex file map item object
class DexMap:

    # Type id definitions
    type_id = {
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
        return '%s[%d] AT %s' % (DexMap.type_id[self.type], self.size,
                hex(self.offset))


# String identifier item object
class DexStrId:

    def __init__(self, byte_data):

        self.offset, = struct.unpack('I', byte_data)

    # Nice string representation
    def __repr__(self):
        return 'string_id_item: %s' % (hex(self.offset))

    # Load corresponding DexStrData object
    def loadStrData(self, dex_file):

        dex_file.seek(self.offset)  # Go to string_data_item

        self.string_data_item = DexStrData(dex_file)


# Type id item object
class DexTypeId:

    def __init__(self, byte_data, str_data):

        self.descriptor_idx, = struct.unpack('I', byte_data)
        self.descriptor = str_data[self.descriptor_idx].data

    def __repr__(self):
        return 'Type: %s' % (self.descriptor)


# Object for string_data_item
class DexStrData:

    def __init__(self, dex_file):

        self.size = DexParser.parseLeb128(dex_file)
        # TODO convert to Modified UTF-8 encoding? (see documentation above)
        self.data = dex_file.read(self.size)

    # Nice string representation
    def __repr__(self):
        return 'ubyte[%d]: %s' % (self.size, self.data)


class DexProtoId:

    def __init__(self, byte_data, str_data, type_data):

        self.shorty_idx, self.return_type_idx, self.parameters_off = struct.unpack('III', byte_data)

        self.shorty_descriptor = str_data[self.shorty_idx].data
        self.return_type = type_data[self.return_type_idx]
        # TODO parse list of parameter types

    # Nice string representation
    def __repr__(self):
        return '%s -> %s' % (self.shorty_descriptor, self.return_type)


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
            self.readStrIds(dex_file)
            self.readStrData(dex_file)
            self.readTypeIds(dex_file)
            self.readProtoIds(dex_file)

    # Parse DEX file map
    def readMap(self, dex_file):

        verb('readMap', 'reading file map at %s' % (hex(self.header.map_off)) )

        dex_file.seek(self.header.map_off)              # Go to the file map
        size, = struct.unpack('I', dex_file.read(4))    # Parse # of elements in the DEX map

        # return array of DexMap objects
        self.map = [ DexMap(dex_file.read(12)) for i in range(size) ]

        verb('readMap', self.map)

    # Parse string identifier list
    def readStrIds(self, dex_file):

        verb('readStrIds', 'reading file map at %s' %
                (hex(self.header.string_ids_off)) )

        dex_file.seek(self.header.string_ids_off)   # Go to string identifiers list

        self.string_ids = [ DexStrId(dex_file.read(4)) for i in
            range(self.header.string_ids_size) ]

        verb('readStrIds', self.string_ids)

    def readStrData(self, dex_file):

        self.string_data = []

        for sid in self.string_ids:
            dex_file.seek(sid.offset)
            self.string_data.append(DexStrData(dex_file))

        verb('readStrData', self.string_data)

    def readTypeIds(self, dex_file):

        dex_file.seek(self.header.type_ids_off)

        self.type_ids = [ DexTypeId(dex_file.read(4), self.string_data) for i in
                range(self.header.type_ids_size) ]

        verb('readTypeIds', self.type_ids)

    def readProtoIds(self, dex_file):

        dex_file.seek(self.header.proto_ids_off)

        self.proto_ids = [ DexProtoId(dex_file.read(12), self.string_data,
            self.type_ids) for i in range(self.header.proto_ids_size) ]

        verb('readProtoIds', self.proto_ids)


    # Method for parsing LEB128 integer values
    # TODO deal with signed values
    @staticmethod
    def parseLeb128(dex_file, signed=False):

        value = 0
        shift = 0

        while True:

            byte, = struct.unpack('B', dex_file.read(1))    # Read byte
            flag = (byte >> 7)      # Parse flag (most significant bit)
            v = (byte & 0x7f)       # Parse payload (bottom 7 bits)
            value += (v << shift)   # Add payload to value
            shift += 7              # Increment shift for next 7-bit payload

            if flag == 0:           # If flag is clear, this is the last byte
                break

        return value


if __name__ == '__main__':

    import sys

    settings.VERBOSE = True

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <DEX file>' % (sys.argv[0]), fatal=True, pre='usage')

    dex_file = sys.argv[1]
    dex = DexParser(dex_file)

