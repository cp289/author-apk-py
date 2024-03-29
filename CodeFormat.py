#!/usr/bin/python3
#
# CodeFormat.py: handle instruction formats
#
# For documentation on Dalvik bytecode, see:
# https://source.android.com/devices/tech/dalvik/dalvik-bytecode.html
# https://source.android.com/devices/tech/dalvik/instruction-formats.html
#

# TODO update CPI format classes to identify which constant pool is used 

from message import *
import struct

# Object for storing various immediate data types
class Format:
    _str = ''
    size = 8
    value = 0
    var_off = 0     # Variable length parameter offset
    var_bits = 4    # Variable length value bit length
    var_length = False
    var_formats = ()
    sub_formats = ()

    # TODO assign variable-length formats their minimum length, then add length
    # parameter to this size
    def __init__(self, intcode, idx):
        if self.var_length:
            var_arg = parseBits(intcode, idx + self.var_off, self.var_bits)
            debug('Format', 'var_arg: %s' % (hex(var_arg)))
            try:
                if self.var_formats[var_arg] is None:
                    self.sub_formats = self.var_formats[-1]
                else:
                    self.sub_formats = self.var_formats[var_arg]
            except IndexError:
                error(self._str, 'invalid variable-length instruction arg: %d' %
                        (var_arg))
                self.sub_formats = self.var_formats[-1]

        self.value = parseBits(intcode, idx, self.size)

    def __repr__(self):
        return '%s:%s' % (self._str, hex(self.value))

# Object for unused formats
class Funused(Format):
    _str = 'UNUSED'
    def __init__(self, intcode, idx):
        super().__init__(intcode, idx)

# Object for zero formats
class Zero(Format):
    _str = 'Zero'
    def __init__(self, intcode, idx):
        pass

# Zero 4 bits
class Z4(Zero):
    size = 4

# Zero 8 bits
class Z8(Zero):
    size = 8

# Zero 12 bits
class Z12(Zero):
    size = 12

# Zero 16 bits
class Z16(Zero):
    size = 16

# Immediate signed nibble
class Imm4(Format):
    _str = 'Imm4'
    size = 4

# Immediate signed byte
class Imm8(Format):
    _str = 'Imm8'
    size = 8

# Immediate signed short
class Imm16(Format):
    _str = 'Imm16'
    size = 16

# Immediate signed int (or float)
class Imm32(Format):
    _str = 'Imm32'
    size = 32

# Immediate signed long (or double)
class Imm64(Format):
    _str = 'Imm64'
    size = 64

# Immediate signed hat (highest 16 bits of 32-bit zeroed reg.)
class ImmHat32(Format):
    _str = 'ImmHat32'
    size = 16

# Immediate signed hat (highest 16 bits of 64-bit zeroed reg.)
class ImmHat64(Format):
    _str = 'ImmHat64'
    size = 16

# Constant pool index (16 bits)
class Cpi16(Format):
    _str = 'Cpi16'
    size = 16

# Constant pool index (32 bits)
class Cpi32(Format):
    _str = 'Cpi32'
    size = 32

# Interface constant
class Intf(Format):
    _str = 'Intf'
    size = 16

# Method constants
class Meth(Format):
    _str = 'Meth'
    size = 16

# Branch target (8 bits)
class Br8(Format):
    _str = 'Br8'
    size = 8

# Branch target (16 bits)
class Br16(Format):
    _str = 'Br16'
    size = 16

# Branch target (32 bits)
class Br32(Format):
    _str = 'Br32'
    size = 32

# Virtual register name (4 bits)
class V4(Format):
    _str = 'V4'
    size = 4

# Virtual register name (8 bits)
class V8(Format):
    _str = 'V8'
    size = 8

# Virtual register name (16 bits)
class V16(Format):
    _str = 'V16'
    size = 16

class F35(Format):
    _str = 'F35'
    var_length = True
    var_off = 4
    var_formats = (
        (Z4, Imm4, Cpi16, Z16),
        (Z4, Imm4, Cpi16, V4, Z12),
        (Z4, Imm4, Cpi16, V4, V4, Z8),
        (Z4, Imm4, Cpi16, V4, V4, V4, Z4),
        (Z4, Imm4, Cpi16, V4, V4, V4, V4),
        (V4, Imm4, Cpi16, V4, V4, V4, V4),
    )

class F45(Format):
    _str = 'F45'
    var_length = True
    var_off = 4
    var_formats = (
        (None),
        (Z4, Imm4, Cpi16, V4, Z12, Cpi16),
        (Z4, Imm4, Cpi16, V4, V4, Z8, Cpi16),
        (Z4, Imm4, Cpi16, V4, V4, V4, Z4, Cpi16),
        (Z4, Imm4, Cpi16, V4, V4, V4, V4, Cpi16),
        (V4, Imm4, Cpi16, V4, V4, V4, V4, Cpi16),
    )

# Returns the least significant n_bits of value
def parseBits(value, idx, n_bits):
    return (value >> idx) & ((1 << n_bits) - 1)

# Instruction type
class Instruction:
    def __init__(self, intcode, idx):
        # Before doing anything, 16-bit align idx
        #idx = (idx + 0xf) & (~0xf)

        self.op = parseBits(intcode, idx, 8)
        debug('Instruction', 'init: %s' % (hex(self.op)))
        self.name = ins_name[self.op]
        self.formats = ins_format[self.op]
        self.idx = idx + 8
        self.fields = tuple(self._getFields(intcode))

        if self.name == 'UNUSED':
            error('Instruction', '%s: read: %s' % (hex(idx), format(self)))

    # Extract instruction fields to self.fields
    def _getFields(self, intcode):
        for fmt in self.formats:
            f = fmt(intcode, self.idx)
            if f.var_length:
                for sub_f in f.sub_formats:
                    debug('_getFields', 'add')
                    field = sub_f(intcode, self.idx)
                    self.idx += sub_f.size
                    yield field
            else:
                self.idx += f.size
                yield f

    def __repr__(self):
        return '%s(%s): %s' % (self.name, hex(self.op), format(self.fields))

# Fixed-length instruction formats
Fwat = (Funused,)
F10x    = (Z8,)
F10t    = (Br8,)
F11x    = (V8,)
F11n    = (V4, V4)
F12x    = (V4, Imm4)
F20t    = (Z8, Br16)
F20bc   = (Imm8, Cpi16)
F21t    = (V8, Br16)
F21s    = (V8, Imm16)
F21h    = (V8, ImmHat32)
F21hw   = (V8, ImmHat64)
F21c    = (V8, Cpi16)
F22x    = (V8, V16)
F22b    = (V8, V8, Imm8)
F22t    = (V4, V4, Br16)
F22s    = (V4, V4, Imm16)
F22c    = (V4, V4, Cpi16)
F22cs   = F22c
F23x    = (V8, V8, V8)
F30t    = (Z8, Br32)
F31i    = (V8, Imm32)
F31t    = (V8, Br32)
F31c    = (V8, Cpi32)
F32x    = (Z8, V16, V16)
F35c    = (F35,)
F35ms   = (F35,)
F35mi   = (F35,)
F3rc    = (Imm8, Cpi16, V16)
F3rms   = (Imm8, Cpi16, V16)
F3rmi   = (Imm8, Cpi16, V16)
F45cc   = (F45,)
F4rcc   = (Imm8, Cpi16, V16, Cpi16)
F51l    = (Imm8, Imm64)

ins_format = {
    0x00 : F10x,
    0x01 : F12x,
    0x02 : F22x,
    0x03 : F32x,
    0x04 : F12x,
    0x05 : F22x,
    0x06 : F32x,
    0x07 : F12x,
    0x08 : F22x,
    0x09 : F32x,
    0x0a : F11x,
    0x0b : F11x,
    0x0c : F11x,
    0x0d : F11x,
    0x0e : F10x,
    0x0f : F11x,
    0x10 : F11x,
    0x11 : F11x,
    0x12 : F11n,
    0x13 : F21s,
    0x14 : F31i,
    0x15 : F21h,
    0x16 : F21s,
    0x17 : F31i,
    0x18 : F51l,
    0x19 : F21h,
    0x1a : F21c,
    0x1b : F31c,
    0x1c : F21c,
    0x1d : F11x,
    0x1e : F11x,
    0x1f : F21c,
    0x20 : F22c,
    0x21 : F12x,
    0x22 : F21c,
    0x23 : F22c,
    0x24 : F35c,
    0x25 : F3rc,
    0x26 : F31t,
    0x27 : F11x,
    0x28 : F10t,
    0x29 : F20t,
    0x2a : F30t,
    0x2b : F31t,
    0x2c : F31t,
    0x2d : F23x,
    0x2e : F23x,
    0x2f : F23x,
    0x30 : F23x,
    0x31 : F23x,
    0x32 : F22t,
    0x33 : F22t,
    0x34 : F22t,
    0x35 : F22t,
    0x36 : F22t,
    0x37 : F22t,
    0x38 : F21t,
    0x39 : F21t,
    0x3a : F21t,
    0x3b : F21t,
    0x3c : F21t,
    0x3d : F21t,
    0x44 : F23x,
    0x45 : F23x,
    0x46 : F23x,
    0x47 : F23x,
    0x48 : F23x,
    0x49 : F23x,
    0x4a : F23x,
    0x4b : F23x,
    0x4c : F23x,
    0x4d : F23x,
    0x4e : F23x,
    0x4f : F23x,
    0x50 : F23x,
    0x51 : F23x,
    0x52 : F22c,
    0x53 : F22c,
    0x54 : F22c,
    0x55 : F22c,
    0x56 : F22c,
    0x57 : F22c,
    0x58 : F22c,
    0x59 : F22c,
    0x5a : F22c,
    0x5b : F22c,
    0x5c : F22c,
    0x5d : F22c,
    0x5e : F22c,
    0x5f : F22c,
    0x60 : F21c,
    0x61 : F21c,
    0x62 : F21c,
    0x63 : F21c,
    0x64 : F21c,
    0x65 : F21c,
    0x66 : F21c,
    0x67 : F21c,
    0x68 : F21c,
    0x69 : F21c,
    0x6a : F21c,
    0x6b : F21c,
    0x6c : F21c,
    0x6d : F21c,
    0x6e : F35c,
    0x6f : F35c,
    0x70 : F35c,
    0x71 : F35c,
    0x72 : F35c,
    0x73 : Fwat,
    0x74 : F3rc,
    0x75 : F3rc,
    0x76 : F3rc,
    0x77 : F3rc,
    0x78 : F3rc,
    0x7b : F12x,
    0x7c : F12x,
    0x7d : F12x,
    0x7e : F12x,
    0x7f : F12x,
    0x80 : F12x,
    0x81 : F12x,
    0x82 : F12x,
    0x83 : F12x,
    0x84 : F12x,
    0x85 : F12x,
    0x86 : F12x,
    0x87 : F12x,
    0x88 : F12x,
    0x89 : F12x,
    0x8a : F12x,
    0x8b : F12x,
    0x8c : F12x,
    0x8d : F12x,
    0x8e : F12x,
    0x8f : F12x,
    0x90 : F23x,
    0x91 : F23x,
    0x92 : F23x,
    0x93 : F23x,
    0x94 : F23x,
    0x95 : F23x,
    0x96 : F23x,
    0x97 : F23x,
    0x98 : F23x,
    0x99 : F23x,
    0x9a : F23x,
    0x9b : F23x,
    0x9c : F23x,
    0x9d : F23x,
    0x9e : F23x,
    0x9f : F23x,
    0xa0 : F23x,
    0xa1 : F23x,
    0xa2 : F23x,
    0xa3 : F23x,
    0xa4 : F23x,
    0xa5 : F23x,
    0xa6 : F23x,
    0xa7 : F23x,
    0xa8 : F23x,
    0xa9 : F23x,
    0xaa : F23x,
    0xab : F23x,
    0xac : F23x,
    0xad : F23x,
    0xae : F23x,
    0xaf : F23x,
    0xb0 : F12x,
    0xb1 : F12x,
    0xb2 : F12x,
    0xb3 : F12x,
    0xb4 : F12x,
    0xb5 : F12x,
    0xb6 : F12x,
    0xb7 : F12x,
    0xb8 : F12x,
    0xb9 : F12x,
    0xba : F12x,
    0xbb : F12x,
    0xbc : F12x,
    0xbd : F12x,
    0xbe : F12x,
    0xbf : F12x,
    0xc0 : F12x,
    0xc1 : F12x,
    0xc2 : F12x,
    0xc3 : F12x,
    0xc4 : F12x,
    0xc5 : F12x,
    0xc6 : F12x,
    0xc7 : F12x,
    0xc8 : F12x,
    0xc9 : F12x,
    0xca : F12x,
    0xcb : F12x,
    0xcc : F12x,
    0xcd : F12x,
    0xce : F12x,
    0xcf : F12x,
    0xd0 : F22s,
    0xd1 : F22s,
    0xd2 : F22s,
    0xd3 : F22s,
    0xd4 : F22s,
    0xd5 : F22s,
    0xd6 : F22s,
    0xd7 : F22s,
    0xd8 : F22b,
    0xd9 : F22b,
    0xda : F22b,
    0xdb : F22b,
    0xdc : F22b,
    0xdd : F22b,
    0xde : F22b,
    0xdf : F22b,
    0xe0 : F22b,
    0xe1 : F22b,
    0xe2 : F22b,
    0xfa : F45cc,   # Dex version >= 038
    0xfb : F4rcc,   # Dex version >= 038
    0xfc : F35c,    # Dex version >= 038
    0xfd : F3rc,    # Dex version >= 038
    0xfe : F21c,    # Dex version >= 039
    0xff : F21c,    # Dex version >= 039
}

ins_name = {
    0x00 : "Nop",
    0x01 : "Mov4_4",
    0x02 : "Mov8_16",
    0x03 : "Mov16_16",
    0x04 : "MovWide4_4",
    0x05 : "MovWide8_16",
    0x06 : "MovWide16_16",
    0x07 : "MovObject4_4",
    0x08 : "MovObject8_16",
    0x09 : "MovObject16_16",
    0x0a : "MovResult",
    0x0b : "MovResultWide",
    0x0c : "MovResultObject",
    0x0d : "MovException",
    0x0e : "ReturnVoid",
    0x0f : "Return",
    0x10 : "ReturnWide",
    0x11 : "ReturnObject",
    0x12 : "Const4",
    0x13 : "Const16",
    0x14 : "Const",
    0x15 : "ConstHigh16",
    0x16 : "ConstWide16",
    0x17 : "ConstWide32",
    0x18 : "ConstWide",
    0x19 : "ConstWideHigh16",
    0x1a : "ConstString",
    0x1b : "ConstStringJumbo",
    0x1c : "ConstClass",
    0x1d : "MonitorEnter",
    0x1e : "MonitorExit",
    0x1f : "CheckCast",
    0x20 : "InstanceOf",
    0x21 : "ArrayLength",
    0x22 : "NewInstance",
    0x23 : "NewArray",
    0x24 : "FilledNewArray",
    0x25 : "FilledNewArrayRange",
    0x26 : "FillArrayData",
    0x27 : "Throw",
    0x28 : "Goto",
    0x29 : "Goto16",
    0x2a : "Goto32",
    0x2b : "PackedSwitch",
    0x2c : "SparseSwitch",
    0x2d : "CmplFloat",
    0x2e : "CmpgFloat",
    0x2f : "CmplDouble",
    0x30 : "CmpgDouble",
    0x31 : "CmpLong",
    0x32 : "IfEq",
    0x33 : "IfNe",
    0x34 : "IfLt",
    0x35 : "IfGe",
    0x36 : "IfGt",
    0x37 : "IfLe",
    0x38 : "IfEqz",
    0x39 : "IfNez",
    0x3a : "IfLtz",
    0x3b : "IfGez",
    0x3c : "IfGtz",
    0x3d : "IfLez",
    0x44 : "Aget",
    0x45 : "AgetWide",
    0x46 : "AgetObject",
    0x47 : "AgetBoolean",
    0x48 : "AgetByte",
    0x49 : "AgetChar",
    0x4a : "AgetShort",
    0x4b : "Aput",
    0x4c : "AputWide",
    0x4d : "AputObject",
    0x4e : "AputBoolean",
    0x4f : "AputByte",
    0x50 : "AputChar",
    0x51 : "AputShort",
    0x52 : "Iget",
    0x53 : "IgetWide",
    0x54 : "IgetObject",
    0x55 : "IgetBoolean",
    0x56 : "IgetByte",
    0x57 : "IgetChar",
    0x58 : "IgetShort",
    0x59 : "Iput",
    0x5a : "IputWide",
    0x5b : "IputObject",
    0x5c : "IputBoolean",
    0x5d : "IputByte",
    0x5e : "IputChar",
    0x5f : "IputShort",
    0x60 : "Sget",
    0x61 : "SgetWide",
    0x62 : "SgetObject",
    0x63 : "SgetBoolean",
    0x64 : "SgetByte",
    0x65 : "SgetChar",
    0x66 : "SgetShort",
    0x67 : "Sput",
    0x68 : "SputWide",
    0x69 : "SputObject",
    0x6a : "SputBoolean",
    0x6b : "SputByte",
    0x6c : "SputChar",
    0x6d : "SputShort",
    0x6e : "InvokeVirtual",
    0x6f : "InvokeSuper",
    0x70 : "InvokeDirect",
    0x71 : "InvokeStatic",
    0x72 : "InvokeInterface",
    0x73 : "UNUSED",
    0x74 : "InvokeVirtualRange",
    0x75 : "InvokeSuperRange",
    0x76 : "InvokeDirectRange",
    0x77 : "InvokeStaticRange",
    0x78 : "InvokeInterfaceRange",
    0x7b : "NegInt",
    0x7c : "NotInt",
    0x7d : "NegLong",
    0x7e : "NotLong",
    0x7f : "NegFloat",
    0x80 : "NegDouble",
    0x81 : "IntToLong",
    0x82 : "IntToFloat",
    0x83 : "IntToDouble",
    0x84 : "LongToInt",
    0x85 : "LongToFloat",
    0x86 : "LongToDouble",
    0x87 : "FloatToInt",
    0x88 : "FloatToLong",
    0x89 : "FloatToDouble",
    0x8a : "DoubleToInt",
    0x8b : "DoubleToLong",
    0x8c : "DoubleToFloat",
    0x8d : "IntToByte",
    0x8e : "IntToChar",
    0x8f : "IntToShort",
    0x90 : "AddInt",
    0x91 : "SubInt",
    0x92 : "MulInt",
    0x93 : "DivInt",
    0x94 : "RemInt",
    0x95 : "AndInt",
    0x96 : "OrInt",
    0x97 : "XorInt",
    0x98 : "ShlInt",
    0x99 : "ShrInt",
    0x9a : "UshrInt",
    0x9b : "AddLong",
    0x9c : "SubLong",
    0x9d : "MulLong",
    0x9e : "DivLong",
    0x9f : "RemLong",
    0xa0 : "AndLong",
    0xa1 : "OrLong",
    0xa2 : "XorLong",
    0xa3 : "ShlLong",
    0xa4 : "ShrLong",
    0xa5 : "UshrLong",
    0xa6 : "AddFloat",
    0xa7 : "SubFloat",
    0xa8 : "MulFloat",
    0xa9 : "DivFloat",
    0xaa : "RemFloat",
    0xab : "AddDouble",
    0xac : "SubDouble",
    0xad : "MulDouble",
    0xae : "DivDouble",
    0xaf : "RemDouble",
    0xb0 : "AddInt2Addr",
    0xb1 : "SubInt2Addr",
    0xb2 : "MulInt2Addr",
    0xb3 : "DivInt2Addr",
    0xb4 : "RemInt2Addr",
    0xb5 : "AndInt2Addr",
    0xb6 : "OrInt2Addr",
    0xb7 : "XorInt2Addr",
    0xb8 : "ShlInt2Addr",
    0xb9 : "ShrInt2Addr",
    0xba : "UshrInt2Addr",
    0xbb : "AddLong2Addr",
    0xbc : "SubLong2Addr",
    0xbd : "MulLong2Addr",
    0xbe : "DivLong2Addr",
    0xbf : "RemLong2Addr",
    0xc0 : "AndLong2Addr",
    0xc1 : "OrLong2Addr",
    0xc2 : "XorLong2Addr",
    0xc3 : "ShlLong2Addr",
    0xc4 : "ShrLong2Addr",
    0xc5 : "UshrLong2Addr",
    0xc6 : "AddFloat2Addr",
    0xc7 : "SubFloat2Addr",
    0xc8 : "MulFloat2Addr",
    0xc9 : "DivFloat2Addr",
    0xca : "RemFloat2Addr",
    0xcb : "AddDouble2Addr",
    0xcc : "SubDouble2Addr",
    0xcd : "MulDouble2Addr",
    0xce : "DivDouble2Addr",
    0xcf : "RemDouble2Addr",
    0xd0 : "AddIntLit16",
    0xd1 : "SubIntLit16",
    0xd2 : "MulIntLit16",
    0xd3 : "DivIntLit16",
    0xd4 : "RemIntLit16",
    0xd5 : "AndIntLit16",
    0xd6 : "OrIntLit16",
    0xd7 : "XorIntLit16",
    0xd8 : "AddIntLit8",
    0xd9 : "SubIntLit8",
    0xda : "MulIntLit8",
    0xdb : "DivIntLit8",
    0xdc : "RemIntLit8",
    0xdd : "AndIntLit8",
    0xde : "OrIntLit8",
    0xdf : "XorIntLit8",
    0xe0 : "ShlIntLit8",
    0xe1 : "ShrIntLit8",
    0xe2 : "UshrIntLit8",
    0xfa : "InvokePolymorphic",         # Dex version >= 038
    0xfb : "InvokePolymorphicRange",    # Dex version >= 038
    0xfc : "InvokeCustom",              # Dex version >= 038
    0xfd : "InvokeCustomRange",         # Dex version >= 038
    0xfe : "ConstMethodHandle",         # Dex version >= 039
    0xff : "ConstMethodType",           # Dex version >= 039
}

# TODO remove all this and use tuple instead of dictionary
# Generate unused instruction handlers
def _push(i):
    ins_name[i] = "UNUSED"
    ins_format[i] = Fwat

for i in range(0x3e, 0x44): _push(i)
for i in range(0x79, 0x7b): _push(i)
for i in range(0xe3, 0xfa): _push(i)

if __name__ == '__main__':

    import sys, settings
    settings.VERBOSE = True
    settings.DEBUG = True
    #settings.DEBUG_FILTER = ('CodeFormat')


    if len(sys.argv) < 2:
        error('CodeFormat', '%s <Bytecode File>' % (sys.argv[0]), pre='usage',
                fatal=True)

