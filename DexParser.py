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
import math


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

        (
            self.file_size,
            self.size,
            self.endian_tag,
            self.link_size,
            self.link_off,
            self.map_off,
            self.string_ids_size,
            self.string_ids_off,
            self.type_ids_size,
            self.type_ids_off,
            self.proto_ids_size,
            self.proto_ids_off,
            self.field_ids_size,
            self.field_ids_off,
            self.method_ids_size,
            self.method_ids_off,
            self.class_defs_size,
            self.class_defs_off,
            self.data_size,
            self.data_off
        ) = struct.unpack('I'*20, dex_file.read(80))


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

    def __init__(self, dex_file):

        (
            self.type,
            self.size,
            self.offset
        ) = struct.unpack('HxxII', dex_file.read(12))

    # Produce nice string formatting of object
    def __repr__(self):

        return '%s[%d] AT %s' % (DexMap.type_id[self.type], self.size,
                hex(self.offset))


# String identifier item object
class DexStrId:

    def __init__(self, dex_file):

        self.offset, = struct.unpack('I', dex_file.read(4))

    # Nice string representation
    def __repr__(self):

        return 'string_id_item: %s' % (hex(self.offset))

    # Load corresponding DexStrData object
    def loadStrData(self, dex_file):

        dex_file.seek(self.offset)  # Go to string_data_item

        self.string_data_item = DexStrData(dex_file)


# Type id item object
class DexTypeId:

    def __init__(self, dex_file, str_data):

        self.descriptor_idx, = struct.unpack('I', dex_file.read(4))
        self.descriptor = str_data[self.descriptor_idx].data

    # String representation
    def __repr__(self):

        return 'Type: %s' % (self.descriptor)


# Object for string_data_item
class DexStrData:

    def __init__(self, dex_file):

        self.size = DexParser.parseLeb128(dex_file)
        # TODO convert from Modified UTF-8 encoding? (see documentation above)
        self.data = dex_file.read(self.size)

    # Nice string representation
    def __repr__(self):

        return 'ubyte[%d]: %s' % (self.size, self.data)


# Object for proto_id_item
class DexProtoId:

    def __init__(self, dex_file, str_data, type_ids):

        (
            self.shorty_idx,
            self.return_type_idx,
            self.parameters_off
        ) = struct.unpack('III', dex_file.read(12))

        self.shorty_descriptor = str_data[self.shorty_idx].data
        self.return_type = type_ids[self.return_type_idx]

        self.parameters = None

    # Nice string representation
    def __repr__(self):

        return '%s -> %s' % (self.shorty_descriptor, self.return_type)

    # Read parameters
    def loadParameters(self, dex_file, type_ids):

        if self.parameters_off != 0:
            debug('loadProtoParams', 'reading proto. params \t@ %s' %
                    (hex(self.parameters_off)))
            dex_file.seek(self.parameters_off)
            self.parameters = DexTypeList(dex_file, type_ids)


# Object for field_id_item
class DexFieldId:

    def __init__(self, dex_file, type_ids, string_data):

        (
            self.class_idx,
            self.type_idx,
            self.name_idx
        ) = struct.unpack('HHI', dex_file.read(8))

        self.clss = type_ids[self.class_idx]
        self.type = type_ids[self.type_idx]
        self.name = string_data[self.name_idx]

    # String representation
    def __repr__(self):

        return 'field: %s' % (self.name)


# Object for method_id_item
class DexMethodId:

    def __init__(self, dex_file, type_ids, proto_ids, string_data):

        (
            self.class_idx,
            self.proto_idx,
            self.name_idx
        ) = struct.unpack('HHI', dex_file.read(8))

        self.type = type_ids[self.class_idx]
        self.prototype = proto_ids[self.proto_idx]
        self.name = string_data[self.name_idx].data

    # String representation
    def __repr__(self):

        return '%s %s (%s)' % (self.type, self.name, self.prototype)


# Object for encoded_field
class DexEncodedField:

    def __init__(self, dex_file, field_ids):

        self.field_idx_diff = DexParser.parseLeb128(dex_file)
        self.access_flags = DexAccessFlags(DexParser.parseLeb128(dex_file))

        self.field = field_ids[self.field_idx_diff]

    # String representation
    def __repr__(self):

        return '%s (%s)' % (self.field, self.access_flags)


# Object for encoded_method
class DexEncodedMethod:

    def __init__(self, dex_file, method_ids):

        self.method_idx_diff = DexParser.parseLeb128(dex_file)
        self.access_flags = DexAccessFlags(DexParser.parseLeb128(dex_file))
        self.code_off = DexParser.parseLeb128(dex_file)

        self.method_id = method_ids[self.method_idx_diff]
        self.code = None

    # String representation
    def __repr__(self):

        return 'method: %s @%s' % (self.method_id, hex(self.code_off))

    # Load code_item
    def loadCode(self, dex_file, type_ids):

        # If code offset is zero, the method is abstract or native
        if self.code_off != 0:
            dex_file.seek(self.code_off)
            self.code = DexCode(dex_file, type_ids)


# Object for access_flags
class DexAccessFlags:

    def __init__(self, flags):

        self.FLAGS = flags
        self.public =       (flags & 1) == 1
        self.private =      ((flags >> 1) & 1) == 1
        self.protected =    ((flags >> 2) & 1) == 1
        self.static =       ((flags >> 3) & 1) == 1
        self.final =        ((flags >> 4) & 1) == 1
        self.synchronized = ((flags >> 5) & 1) == 1     # For methods
        self.volatile =     ((flags >> 6) & 1) == 1     # For fields
        self.bridge =       self.volatile               # For methods
        self.transient =    ((flags >> 7) & 1) == 1     # For fields
        self.varargs =      self.transient              # For methods
        self.native =       ((flags >> 8) & 1) == 1     # For methods
        self.interface =    ((flags >> 9) & 1) == 1     # For classes
        self.abstract =     ((flags >> 10) & 1) == 1    # For classes, fields
        self.strict =       ((flags >> 11) & 1) == 1    # For fields
        self.synthetic =    ((flags >> 12) & 1) == 1
        self.annotation =   ((flags >> 13) & 1) == 1    # For classes
        self.enum =         ((flags >> 14) & 1) == 1    # For classes, fields
        # NOTE bit 15 is unused
        self.constructor =  ((flags >> 16) & 1) == 1    # For methods
        self.declared_synchronized = ((flags >> 17) & 1) == 1   # For methods

    # Represent object as hex string
    def __repr__(self):

        return 'AccessFlags:%s' % (hex(self.FLAGS))


# Object for type_list
class DexTypeList:

    def __init__(self, dex_file, type_ids):

        self.size, = struct.unpack('I', dex_file.read(4))
        self.type_idxs = struct.unpack('H'*self.size, dex_file.read(2*self.size))
        self.types = [ type_ids[i] for i in self.type_idxs ]

    # String representation
    def __repr__(self):

        return '%s' % (self.types)


# Object for class_data_item
class DexClassData:

    def __init__(self, dex_file, type_ids, field_ids, method_ids):

        self.static_fields_size = DexParser.parseLeb128(dex_file)
        self.instance_fields_size = DexParser.parseLeb128(dex_file)
        self.direct_methods_size = DexParser.parseLeb128(dex_file)
        self.virtual_methods_size = DexParser.parseLeb128(dex_file)

        self.static_fields = []
        self.instance_fields = []
        self.direct_methods = []
        self.virtual_methods = []

        for i in range(self.static_fields_size):
            self.static_fields.append(DexEncodedField(dex_file, field_ids))

        for i in range(self.instance_fields_size):
            self.instance_fields.append(DexEncodedField(dex_file, field_ids))

        for i in range(self.direct_methods_size):
            self.direct_methods.append(DexEncodedMethod(dex_file, method_ids))

        for i in range(self.virtual_methods_size):
            self.virtual_methods.append(DexEncodedMethod(dex_file, method_ids))

        for m in self.direct_methods:
            m.loadCode(dex_file, type_ids)

        for m in self.virtual_methods:
            m.loadCode(dex_file, type_ids)

    # String representation
    def __repr__(self):

        return 'ClassData:(%d,%d,%d,%d)' % (self.static_fields_size,
                self.instance_fields_size, self.direct_methods_size,
                self.virtual_methods_size)


# Object for class_def_item
class DexClassDef:

    def __init__(self, dex_file, type_ids, string_data):

        (
            self.class_idx,
            self.flags,
            self.superclass_idx,
            self.interfaces_off,
            self.source_file_idx,
            self.annotations_off,
            self.class_data_off,
            self.static_values_off
        ) = struct.unpack('IIIIIIII', dex_file.read(32))

        self.type_id = type_ids[self.class_idx]
        self.access_flags = DexAccessFlags(self.flags)

        self.interfaces = None
        self.class_data = None

        if self.superclass_idx != DexParser.NO_INDEX:
            self.superclass = type_ids[self.superclass_idx]
        else:
            self.superclass = None

        if self.source_file_idx != DexParser.NO_INDEX:
            self.source_file = string_data[self.source_file_idx].data
        else:
            self.source_file = None

        if self.annotations_off != 0:
            # TODO parse annotations_directory_item
            self.annotations = None
        else:
            self.annotations = None

        if self.static_values_off != 0:
            # TODO parse encoded_array_item
            self.static_values = None
        else:
            self.static_values = None

    # String representation
    def __repr__(self):

        return 'class: %s->%s' % (self.superclass, self.type_id)

    # Load interfaces type_list
    def loadInterfaces(self, dex_file, type_ids):

        if self.interfaces_off != 0:
            dex_file.seek(self.interfaces_off)
            self.interfaces = DexTypeList(dex_file, type_ids)

    # Load class_data_item
    def loadClassData(self, dex_file, type_ids, field_ids, method_ids):

        if self.class_data_off != 0:
            dex_file.seek(self.class_data_off)
            self.class_data = DexClassData(dex_file, type_ids, field_ids, method_ids)


# Object for try_item
class DexTry:

    def __init__(self, dex_file):

        (
            self.start_addr,
            self.insn_count,
            self.handler_off
        ) = struct.unpack('IHH', dex_file.read(8))

    # String representation
    def __repr__(self):

        return 'Try:byte[%d]@%s' % (self.insn_count, self.start_addr)


# Object for encoded_type_addr_pair
class DexHandler:

    def __init__(self, dex_file, type_ids):

        self.type_idx = DexParser.parseLeb128(dex_file)
        self.type = type_ids[self.type_idx]
        self.addr = DexParser.parseLeb128(dex_file)

    # String representation
    def __repr__(self):

        return 'Handler:%s@%s' % (self.type, self.addr)


# Object for encoded_catch_handler
class DexCatchHandler:

    def __init__(self, dex_file, type_ids):

        self.size = DexParser.parseLeb128(dex_file, signed=True)
        self.handlers = []
        self.catch_all_addr = None

        for i in range(abs(self.size)):
            self.handlers.append(DexHandler(dex_file, type_ids))

        if self.size <= 0:
            self.catch_all_addr = DexParser.parseLeb128(dex_file)
            self.CATCH_ALL = True

    # String representation
    def __repr__(self):

        msg = 'w/catchAll' if self.CATCH_ALL else ''
        return 'Catch:Handler[%d]%s' % (abs(self.size), msg)


# Object for code_item
class DexCode:

    def __init__(self, dex_file, type_ids):

        (
            self.registers_size,
            self.ins_size,
            self.outs_size,
            self.tries_size,
            self.debug_info_off,
            self.insns_size
        ) = struct.unpack('HHHHII', dex_file.read(16))

        self.insns = struct.unpack('H'*self.insns_size,
                dex_file.read(self.insns_size*2))

        # Move to 4-byte aligned offset
        dex_file.seek( (dex_file.tell() + 0x3) & ~0x3 )

        self.tries = []
        self.handlers = []
        self.handlers_size = 0

        if self.tries_size != 0:
            for i in range(self.tries_size):
                self.tries.append(DexTry(dex_file))

            self.handlers_size = DexParser.parseLeb128(dex_file)
            for i in range(self.handlers_size):
                self.handlers.append(DexCatchHandler(dex_file, type_ids))


# Object to manage all DEX parsing operations/data
class DexParser:

    NO_INDEX = int('0xffffffff', 16)

    def __init__(self, dex_file_path):

        self.FILE_PATH = dex_file_path

        with open(self.FILE_PATH, 'rb') as dex_file:

            self.readHeader(dex_file)
            self.readMap(dex_file)
            self.readStrIds(dex_file)
            self.readStrData(dex_file)
            self.readTypeIds(dex_file)
            self.readProtoIds(dex_file)
            self.readProtoParams(dex_file)
            self.readFieldIds(dex_file)
            self.readMethodIds(dex_file)
            self.readClassDefs(dex_file)
            self.readInterfaces(dex_file)
            self.readClassData(dex_file)

    # Parse DEX file header
    def readHeader(self, dex_file):
        self.header = DexHeader(dex_file)

        # Verify header magic and report DEX version
        if self.header.VALID:
            verb('readHeader', 'found DEX v.%d header for %s' %
                    (self.header.VERSION, self.FILE_PATH))
        else:
            error('readHeader', 'invalid DEX header magic for %s' %
                    (self.FILE_PATH))
            return

        # Check file endianness
        if self.header.endian_tag == int('0x78563412', 16):
            warn('readHeader', 'found reversed endian tag in %s' %
                    (dex_file_path))
            error('readHeader', 'reversed endian parsing not implemented',
                    fatal=True)
        elif self.header.endian_tag != int('0x12345678', 16):
            error('readHeader', 'found invalid endian tag for %s' %
                    (dex_file_path))

    # Parse DEX file map
    def readMap(self, dex_file):

        verb('readMap', 'reading file map \t\t@ %s' % (hex(self.header.map_off)) )

        dex_file.seek(self.header.map_off)              # Go to the file map
        size, = struct.unpack('I', dex_file.read(4))    # Parse # of elements in the DEX map

        # return array of DexMap objects
        self.map = [ DexMap(dex_file) for i in range(size) ]

    # Parse string identifier list
    def readStrIds(self, dex_file):

        verb('readStrIds', 'reading string ids \t\t@ %s' %
                (hex(self.header.string_ids_off)) )

        dex_file.seek(self.header.string_ids_off)   # Go to string identifiers list

        self.string_ids = [ DexStrId(dex_file) for i in
                range(self.header.string_ids_size) ]

    # Parse string data
    def readStrData(self, dex_file):

        verb('readStrData', 'reading string data \t@ %s' %
                (hex(self.string_ids[0].offset)))

        self.string_data = []
        for sid in self.string_ids:
            dex_file.seek(sid.offset)
            self.string_data.append(DexStrData(dex_file))

    # Parse type ids
    def readTypeIds(self, dex_file):

        verb('readTypeIds', 'reading type ids \t\t@ %s' %
                (hex(self.header.type_ids_off)))

        dex_file.seek(self.header.type_ids_off)

        self.type_ids = [ DexTypeId(dex_file, self.string_data) for i in
                range(self.header.type_ids_size) ]

    # Parse prototype ids
    def readProtoIds(self, dex_file):

        verb('readProtoIds', 'reading prototype ids \t@ %s' %
                (hex(self.header.proto_ids_off)))

        dex_file.seek(self.header.proto_ids_off)

        self.proto_ids = [ DexProtoId(dex_file, self.string_data, self.type_ids)
                for i in range(self.header.proto_ids_size) ]

    # Parse prototype parameters
    def readProtoParams(self, dex_file):

        for p in self.proto_ids:
            p.loadParameters(dex_file, self.type_ids)

    # Parse field ids
    def readFieldIds(self, dex_file):

        verb('readFieldIds', 'reading field ids \t@ %s' %
                (hex(self.header.field_ids_off)))

        dex_file.seek(self.header.field_ids_off)

        self.field_ids = [ DexFieldId(dex_file, self.type_ids, self.string_data)
                for i in range(self.header.field_ids_size) ]

    # Parse method ids
    def readMethodIds(self, dex_file):

        verb('readMethodIds', 'reading method ids \t@ %s' %
                (hex(self.header.method_ids_off)))

        dex_file.seek(self.header.method_ids_off)

        self.method_ids = [ DexMethodId(dex_file, self.type_ids, self.proto_ids,
            self.string_data) for i in range(self.header.method_ids_size) ]

    # Parse class definitions
    def readClassDefs(self, dex_file):

        verb('readClassDefs', 'reading class defs \t@ %s' %
                (hex(self.header.class_defs_off)))

        dex_file.seek(self.header.class_defs_off)

        self.class_defs = [ DexClassDef(dex_file, self.type_ids,
            self.string_data) for i in range(self.header.class_defs_size) ]

    # Parse interfaces
    def readInterfaces(self, dex_file):

        for c in self.class_defs:
            c.loadClassData(dex_file, self.type_ids, self.field_ids, self.method_ids)

    # Parse class data
    def readClassData(self, dex_file):

        for c in self.class_defs:
            c.loadClassData(dex_file, self.type_ids, self.field_ids, self.method_ids)


    # Method for parsing LEB128 integer values from files
    @staticmethod
    def parseLeb128(dex_file, signed=False):

        byte_data = []

        for i in range(5):  # NOTE LEB128 is at most 5 bytes in DEX format

            byte, = struct.unpack('B', dex_file.read(1))    # Read byte
            byte_data.append(byte)
            flag = (byte >> 7)      # Parse flag (most significant bit)
            if flag == 0:           # If flag is clear, this is the last byte
                break

        return DexParser.leb128(byte_data, signed)

    # Parse LEB128 value from POSITIVE integer
    @staticmethod
    def numLeb128(num, signed=False):

        n_bytes = math.ceil(num.bit_length()/8)
        print(n_bytes)
        byte_data = tuple(num.to_bytes(n_bytes, 'little'))
        print(byte_data)
        return DexParser.leb128(byte_data, signed)

    # Parse LEB128 value from byte array
    @staticmethod
    def leb128(byte_data, signed=False):

        value = 0
        shift = 0

        for byte in byte_data:

            flag = (byte >> 7)      # Parse flag (most significant bit)
            v = (byte & 0x7f)       # Parse payload (bottom 7 bits)
            value += (v << shift)   # Add payload to value
            shift += 7              # Increment shift for next 7-bit payload

            if flag == 0:           # If flag is clear, this is the last byte
                break

        if signed and value >= (1 << (shift-1)):
            value -= (1 << shift)

        return value


if __name__ == '__main__':

    import sys
    import settings

    settings.VERBOSE = True
    settings.DEBUG = True
    settings.DEBUG_FILTER = ('loadProtoParams')

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <DEX file>' % (sys.argv[0]), fatal=True, pre='usage')

    dex_file = sys.argv[1]
    dex = DexParser(dex_file)

