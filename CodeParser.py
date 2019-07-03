#!/usr/bin/python3
#
# CodeParser.py: Object to parse Dalvik bytecode
#
# For documentation on Dalvik bytecode, see:
# https://source.android.com/devices/tech/dalvik/dalvik-bytecode.html
# https://source.android.com/devices/tech/dalvik/instruction-formats.html
#
# TODO make inheritance based on instruction type to save time

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

class Nop:
    def __init__(self, bytecode, idx):
        pass
class Mov4_4:
    def __init__(self, bytecode, idx):
        pass
class Mov8_16:
    def __init__(self, bytecode, idx):
        pass
class Mov16_16:
    def __init__(self, bytecode, idx):
        pass
class MovWide4_4:
    def __init__(self, bytecode, idx):
        pass
class MovWide8_16:
    def __init__(self, bytecode, idx):
        pass
class MovWide16_16:
    def __init__(self, bytecode, idx):
        pass
class MovObject4_4:
    def __init__(self, bytecode, idx):
        pass
class MovObject8_16:
    def __init__(self, bytecode, idx):
        pass
class MovObject16_16:
    def __init__(self, bytecode, idx):
        pass
class MovResult:
    def __init__(self, bytecode, idx):
        pass
class MovResultWide:
    def __init__(self, bytecode, idx):
        pass
class MovResultObject:
    def __init__(self, bytecode, idx):
        pass
class MovException:
    def __init__(self, bytecode, idx):
        pass
class ReturnVoid:
    def __init__(self, bytecode, idx):
        pass
class Return:
    def __init__(self, bytecode, idx):
        pass
class ReturnWide:
    def __init__(self, bytecode, idx):
        pass
class ReturnObject:
    def __init__(self, bytecode, idx):
        pass
class Const4:
    def __init__(self, bytecode, idx):
        pass
class Const16:
    def __init__(self, bytecode, idx):
        pass
class Const:
    def __init__(self, bytecode, idx):
        pass
class ConstHigh16:
    def __init__(self, bytecode, idx):
        pass
class ConstWide16:
    def __init__(self, bytecode, idx):
        pass
class ConstWide32:
    def __init__(self, bytecode, idx):
        pass
class ConstWide:
    def __init__(self, bytecode, idx):
        pass
class ConstWideHigh16:
    def __init__(self, bytecode, idx):
        pass
class ConstString:
    def __init__(self, bytecode, idx):
        pass
class ConstStringJumbo:
    def __init__(self, bytecode, idx):
        pass
class ConstClass:
    def __init__(self, bytecode, idx):
        pass
class MonitorEnter:
    def __init__(self, bytecode, idx):
        pass
class MonitorExit:
    def __init__(self, bytecode, idx):
        pass
class CheckCast:
    def __init__(self, bytecode, idx):
        pass
class InstanceOf:
    def __init__(self, bytecode, idx):
        pass
class ArrayLength:
    def __init__(self, bytecode, idx):
        pass
class NewInstance:
    def __init__(self, bytecode, idx):
        pass
class NewArray:
    def __init__(self, bytecode, idx):
        pass
class FilledNewArray:
    def __init__(self, bytecode, idx):
        pass
class FilledNewArrayRange:
    def __init__(self, bytecode, idx):
        pass
class FillArrayData:
    def __init__(self, bytecode, idx):
        pass
class Throw:
    def __init__(self, bytecode, idx):
        pass
class Goto:
    def __init__(self, bytecode, idx):
        pass
class Goto16:
    def __init__(self, bytecode, idx):
        pass
class Goto32:
    def __init__(self, bytecode, idx):
        pass
class PackedSwitch:
    def __init__(self, bytecode, idx):
        pass
class SparseSwitch:
    def __init__(self, bytecode, idx):
        pass
class CmplFloat:
    def __init__(self, bytecode, idx):
        pass
class CmpgFloat:
    def __init__(self, bytecode, idx):
        pass
class CmplDouble:
    def __init__(self, bytecode, idx):
        pass
class CmpgDouble:
    def __init__(self, bytecode, idx):
        pass
class CmpLong:
    def __init__(self, bytecode, idx):
        pass
class IfEq:
    def __init__(self, bytecode, idx):
        pass
class IfNe:
    def __init__(self, bytecode, idx):
        pass
class IfLt:
    def __init__(self, bytecode, idx):
        pass
class IfGe:
    def __init__(self, bytecode, idx):
        pass
class IfGt:
    def __init__(self, bytecode, idx):
        pass
class IfLe:
    def __init__(self, bytecode, idx):
        pass
class IfEqz:
    def __init__(self, bytecode, idx):
        pass
class IfNez:
    def __init__(self, bytecode, idx):
        pass
class IfLtz:
    def __init__(self, bytecode, idx):
        pass
class IfGez:
    def __init__(self, bytecode, idx):
        pass
class IfGtz:
    def __init__(self, bytecode, idx):
        pass
class IfLez:
    def __init__(self, bytecode, idx):
        pass
class Aget:
    def __init__(self, bytecode, idx):
        pass
class AgetWide:
    def __init__(self, bytecode, idx):
        pass
class AgetObject:
    def __init__(self, bytecode, idx):
        pass
class AgetBoolean:
    def __init__(self, bytecode, idx):
        pass
class AgetByte:
    def __init__(self, bytecode, idx):
        pass
class AgetChar:
    def __init__(self, bytecode, idx):
        pass
class AgetShort:
    def __init__(self, bytecode, idx):
        pass
class Aput:
    def __init__(self, bytecode, idx):
        pass
class AputWide:
    def __init__(self, bytecode, idx):
        pass
class AputObject:
    def __init__(self, bytecode, idx):
        pass
class AputBoolean:
    def __init__(self, bytecode, idx):
        pass
class AputByte:
    def __init__(self, bytecode, idx):
        pass
class AputChar:
    def __init__(self, bytecode, idx):
        pass
class AputShort:
    def __init__(self, bytecode, idx):
        pass
class Iget:
    def __init__(self, bytecode, idx):
        pass
class IgetWide:
    def __init__(self, bytecode, idx):
        pass
class IgetObject:
    def __init__(self, bytecode, idx):
        pass
class IgetBoolean:
    def __init__(self, bytecode, idx):
        pass
class IgetByte:
    def __init__(self, bytecode, idx):
        pass
class IgetChar:
    def __init__(self, bytecode, idx):
        pass
class IgetShort:
    def __init__(self, bytecode, idx):
        pass
class Iput:
    def __init__(self, bytecode, idx):
        pass
class IputWide:
    def __init__(self, bytecode, idx):
        pass
class IputObject:
    def __init__(self, bytecode, idx):
        pass
class IputBoolean:
    def __init__(self, bytecode, idx):
        pass
class IputByte:
    def __init__(self, bytecode, idx):
        pass
class IputChar:
    def __init__(self, bytecode, idx):
        pass
class IputShort:
    def __init__(self, bytecode, idx):
        pass
class Sget:
    def __init__(self, bytecode, idx):
        pass
class SgetWide:
    def __init__(self, bytecode, idx):
        pass
class SgetObject:
    def __init__(self, bytecode, idx):
        pass
class SgetBoolean:
    def __init__(self, bytecode, idx):
        pass
class SgetByte:
    def __init__(self, bytecode, idx):
        pass
class SgetChar:
    def __init__(self, bytecode, idx):
        pass
class SgetShort:
    def __init__(self, bytecode, idx):
        pass
class Sput:
    def __init__(self, bytecode, idx):
        pass
class SputWide:
    def __init__(self, bytecode, idx):
        pass
class SputObject:
    def __init__(self, bytecode, idx):
        pass
class SputBoolean:
    def __init__(self, bytecode, idx):
        pass
class SputByte:
    def __init__(self, bytecode, idx):
        pass
class SputChar:
    def __init__(self, bytecode, idx):
        pass
class SputShort:
    def __init__(self, bytecode, idx):
        pass
class InvokeVirtual:
    def __init__(self, bytecode, idx):
        pass
class InvokeSuper:
    def __init__(self, bytecode, idx):
        pass
class InvokeDirect:
    def __init__(self, bytecode, idx):
        pass
class InvokeStatic:
    def __init__(self, bytecode, idx):
        pass
class InvokeInterface:
    def __init__(self, bytecode, idx):
        pass
class InvokeVirtualRange:
    def __init__(self, bytecode, idx):
        pass
class InvokeSuperRange:
    def __init__(self, bytecode, idx):
        pass
class InvokeDirectRange:
    def __init__(self, bytecode, idx):
        pass
class InvokeStaticRange:
    def __init__(self, bytecode, idx):
        pass
class InvokeInterfaceRange:
    def __init__(self, bytecode, idx):
        pass
class NegInt:
    def __init__(self, bytecode, idx):
        pass
class NotInt:
    def __init__(self, bytecode, idx):
        pass
class NegLong:
    def __init__(self, bytecode, idx):
        pass
class NotLong:
    def __init__(self, bytecode, idx):
        pass
class NegFloat:
    def __init__(self, bytecode, idx):
        pass
class NegDouble:
    def __init__(self, bytecode, idx):
        pass
class IntToLong:
    def __init__(self, bytecode, idx):
        pass
class IntToFloat:
    def __init__(self, bytecode, idx):
        pass
class IntToDouble:
    def __init__(self, bytecode, idx):
        pass
class LongToInt:
    def __init__(self, bytecode, idx):
        pass
class LongToFloat:
    def __init__(self, bytecode, idx):
        pass
class LongToDouble:
    def __init__(self, bytecode, idx):
        pass
class FloatToInt:
    def __init__(self, bytecode, idx):
        pass
class FloatToLong:
    def __init__(self, bytecode, idx):
        pass
class FloatToDouble:
    def __init__(self, bytecode, idx):
        pass
class DoubleToInt:
    def __init__(self, bytecode, idx):
        pass
class DoubleToLong:
    def __init__(self, bytecode, idx):
        pass
class DoubleToFloat:
    def __init__(self, bytecode, idx):
        pass
class IntToByte:
    def __init__(self, bytecode, idx):
        pass
class IntToChar:
    def __init__(self, bytecode, idx):
        pass
class IntToShort:
    def __init__(self, bytecode, idx):
        pass
class AddInt:
    def __init__(self, bytecode, idx):
        pass
class SubInt:
    def __init__(self, bytecode, idx):
        pass
class MulInt:
    def __init__(self, bytecode, idx):
        pass
class DivInt:
    def __init__(self, bytecode, idx):
        pass
class RemInt:
    def __init__(self, bytecode, idx):
        pass
class AndInt:
    def __init__(self, bytecode, idx):
        pass
class OrInt:
    def __init__(self, bytecode, idx):
        pass
class XorInt:
    def __init__(self, bytecode, idx):
        pass
class ShlInt:
    def __init__(self, bytecode, idx):
        pass
class ShrInt:
    def __init__(self, bytecode, idx):
        pass
class UshrInt:
    def __init__(self, bytecode, idx):
        pass
class AddLong:
    def __init__(self, bytecode, idx):
        pass
class SubLong:
    def __init__(self, bytecode, idx):
        pass
class MulLong:
    def __init__(self, bytecode, idx):
        pass
class DivLong:
    def __init__(self, bytecode, idx):
        pass
class RemLong:
    def __init__(self, bytecode, idx):
        pass
class AndLong:
    def __init__(self, bytecode, idx):
        pass
class OrLong:
    def __init__(self, bytecode, idx):
        pass
class XorLong:
    def __init__(self, bytecode, idx):
        pass
class ShlLong:
    def __init__(self, bytecode, idx):
        pass
class ShrLong:
    def __init__(self, bytecode, idx):
        pass
class UshrLong:
    def __init__(self, bytecode, idx):
        pass
class AddFloat:
    def __init__(self, bytecode, idx):
        pass
class SubFloat:
    def __init__(self, bytecode, idx):
        pass
class MulFloat:
    def __init__(self, bytecode, idx):
        pass
class DivFloat:
    def __init__(self, bytecode, idx):
        pass
class RemFloat:
    def __init__(self, bytecode, idx):
        pass
class AddDouble:
    def __init__(self, bytecode, idx):
        pass
class SubDouble:
    def __init__(self, bytecode, idx):
        pass
class MulDouble:
    def __init__(self, bytecode, idx):
        pass
class DivDouble:
    def __init__(self, bytecode, idx):
        pass
class RemDouble:
    def __init__(self, bytecode, idx):
        pass
class AddInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class SubInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class MulInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class DivInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class RemInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class AndInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class OrInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class XorInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class ShlInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class ShrInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class UshrInt2Addr:
    def __init__(self, bytecode, idx):
        pass
class AddLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class SubLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class MulLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class DivLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class RemLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class AndLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class OrLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class XorLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class ShlLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class ShrLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class UshrLong2Addr:
    def __init__(self, bytecode, idx):
        pass
class AddFloat2Addr:
    def __init__(self, bytecode, idx):
        pass
class SubFloat2Addr:
    def __init__(self, bytecode, idx):
        pass
class MulFloat2Addr:
    def __init__(self, bytecode, idx):
        pass
class DivFloat2Addr:
    def __init__(self, bytecode, idx):
        pass
class RemFloat2Addr:
    def __init__(self, bytecode, idx):
        pass
class AddDouble2Addr:
    def __init__(self, bytecode, idx):
        pass
class SubDouble2Addr:
    def __init__(self, bytecode, idx):
        pass
class MulDouble2Addr:
    def __init__(self, bytecode, idx):
        pass
class DivDouble2Addr:
    def __init__(self, bytecode, idx):
        pass
class RemDouble2Addr:
    def __init__(self, bytecode, idx):
        pass
class AddIntLit16:
    def __init__(self, bytecode, idx):
        pass
class SubIntLit16:
    def __init__(self, bytecode, idx):
        pass
class MulIntLit16:
    def __init__(self, bytecode, idx):
        pass
class DivIntLit16:
    def __init__(self, bytecode, idx):
        pass
class RemIntLit16:
    def __init__(self, bytecode, idx):
        pass
class AndIntLit16:
    def __init__(self, bytecode, idx):
        pass
class OrIntLit16:
    def __init__(self, bytecode, idx):
        pass
class XorIntLit16:
    def __init__(self, bytecode, idx):
        pass
class AddIntLit8:
    def __init__(self, bytecode, idx):
        pass
class SubIntLit8:
    def __init__(self, bytecode, idx):
        pass
class MulIntLit8:
    def __init__(self, bytecode, idx):
        pass
class DivIntLit8:
    def __init__(self, bytecode, idx):
        pass
class RemIntLit8:
    def __init__(self, bytecode, idx):
        pass
class AndIntLit8:
    def __init__(self, bytecode, idx):
        pass
class OrIntLit8:
    def __init__(self, bytecode, idx):
        pass
class XorIntLit8:
    def __init__(self, bytecode, idx):
        pass
class ShlIntLit8:
    def __init__(self, bytecode, idx):
        pass
class ShrIntLit8:
    def __init__(self, bytecode, idx):
        pass
class UshrIntLit8:
    def __init__(self, bytecode, idx):
        pass
class InvokePolymorphic:
    def __init__(self, bytecode, idx):
        pass
class InvokePolymorphicRange:
    def __init__(self, bytecode, idx):
        pass
class InvokeCustom:
    def __init__(self, bytecode, idx):
        pass
class InvokeCustomRange:
    def __init__(self, bytecode, idx):
        pass
class ConstMethodHandle:
    def __init__(self, bytecode, idx):
        pass
class ConstMethodType:
    def __init__(self, bytecode, idx):
        pass


# Object for parsing Dalvik bytecode
class CodeParser:

    instr = {
        0x00 : Nop,
        0x01 : Mov4_4,
        0x02 : Mov8_16,
        0x03 : Mov16_16,
        0x04 : MovWide4_4,
        0x05 : MovWide8_16,
        0x06 : MovWide16_16,
        0x07 : MovObject4_4,
        0x08 : MovObject8_16,
        0x09 : MovObject16_16,
        0x0a : MovResult,
        0x0b : MovResultWide,
        0x0c : MovResultObject,
        0x0d : MovException,
        0x0e : ReturnVoid,
        0x0f : Return,
        0x10 : ReturnWide,
        0x11 : ReturnObject,
        0x12 : Const4,
        0x13 : Const16,
        0x14 : Const,
        0x15 : ConstHigh16,
        0x16 : ConstWide16,
        0x17 : ConstWide32,
        0x18 : ConstWide,
        0x19 : ConstWideHigh16,
        0x1a : ConstString,
        0x1b : ConstStringJumbo,
        0x1c : ConstClass,
        0x1d : MonitorEnter,
        0x1e : MonitorExit,
        0x1f : CheckCast,
        0x20 : InstanceOf,
        0x21 : ArrayLength,
        0x22 : NewInstance,
        0x23 : NewArray,
        0x24 : FilledNewArray,
        0x25 : FilledNewArrayRange,
        0x26 : FillArrayData,
        0x27 : Throw,
        0x28 : Goto,
        0x29 : Goto16,
        0x2a : Goto32,
        0x2b : PackedSwitch,
        0x2c : SparseSwitch,
        0x2d : CmplFloat,
        0x2e : CmpgFloat,
        0x2f : CmplDouble,
        0x30 : CmpgDouble,
        0x31 : CmpLong,
        0x32 : IfEq,
        0x33 : IfNe,
        0x34 : IfLt,
        0x35 : IfGe,
        0x36 : IfGt,
        0x37 : IfLe,
        0x38 : IfEqz,
        0x39 : IfNez,
        0x3a : IfLtz,
        0x3b : IfGez,
        0x3c : IfGtz,
        0x3d : IfLez,
        0x44 : Aget,
        0x45 : AgetWide,
        0x46 : AgetObject,
        0x47 : AgetBoolean,
        0x48 : AgetByte,
        0x49 : AgetChar,
        0x4a : AgetShort,
        0x4b : Aput,
        0x4c : AputWide,
        0x4d : AputObject,
        0x4e : AputBoolean,
        0x4f : AputByte,
        0x50 : AputChar,
        0x51 : AputShort,
        0x52 : Iget,
        0x53 : IgetWide,
        0x54 : IgetObject,
        0x55 : IgetBoolean,
        0x56 : IgetByte,
        0x57 : IgetChar,
        0x58 : IgetShort,
        0x59 : Iput,
        0x5a : IputWide,
        0x5b : IputObject,
        0x5c : IputBoolean,
        0x5d : IputByte,
        0x5e : IputChar,
        0x5f : IputShort,
        0x60 : Sget,
        0x61 : SgetWide,
        0x62 : SgetObject,
        0x63 : SgetBoolean,
        0x64 : SgetByte,
        0x65 : SgetChar,
        0x66 : SgetShort,
        0x67 : Sput,
        0x68 : SputWide,
        0x69 : SputObject,
        0x6a : SputBoolean,
        0x6b : SputByte,
        0x6c : SputChar,
        0x6d : SputShort,
        0x6e : InvokeVirtual,
        0x6f : InvokeSuper,
        0x70 : InvokeDirect,
        0x71 : InvokeStatic,
        0x72 : InvokeInterface,
        0x74 : InvokeVirtualRange,
        0x75 : InvokeSuperRange,
        0x76 : InvokeDirectRange,
        0x77 : InvokeStaticRange,
        0x78 : InvokeInterfaceRange,
        0x7b : NegInt,
        0x7c : NotInt,
        0x7d : NegLong,
        0x7e : NotLong,
        0x7f : NegFloat,
        0x80 : NegDouble,
        0x81 : IntToLong,
        0x82 : IntToFloat,
        0x83 : IntToDouble,
        0x84 : LongToInt,
        0x85 : LongToFloat,
        0x86 : LongToDouble,
        0x87 : FloatToInt,
        0x88 : FloatToLong,
        0x89 : FloatToDouble,
        0x8a : DoubleToInt,
        0x8b : DoubleToLong,
        0x8c : DoubleToFloat,
        0x8d : IntToByte,
        0x8e : IntToChar,
        0x8f : IntToShort,
        0x90 : AddInt,
        0x91 : SubInt,
        0x92 : MulInt,
        0x93 : DivInt,
        0x94 : RemInt,
        0x95 : AndInt,
        0x96 : OrInt,
        0x97 : XorInt,
        0x98 : ShlInt,
        0x99 : ShrInt,
        0x9a : UshrInt,
        0x9b : AddLong,
        0x9c : SubLong,
        0x9d : MulLong,
        0x9e : DivLong,
        0x9f : RemLong,
        0xa0 : AndLong,
        0xa1 : OrLong,
        0xa2 : XorLong,
        0xa3 : ShlLong,
        0xa4 : ShrLong,
        0xa5 : UshrLong,
        0xa6 : AddFloat,
        0xa7 : SubFloat,
        0xa8 : MulFloat,
        0xa9 : DivFloat,
        0xaa : RemFloat,
        0xab : AddDouble,
        0xac : SubDouble,
        0xad : MulDouble,
        0xae : DivDouble,
        0xaf : RemDouble,
        0xb0 : AddInt2Addr,
        0xb1 : SubInt2Addr,
        0xb2 : MulInt2Addr,
        0xb3 : DivInt2Addr,
        0xb4 : RemInt2Addr,
        0xb5 : AndInt2Addr,
        0xb6 : OrInt2Addr,
        0xb7 : XorInt2Addr,
        0xb8 : ShlInt2Addr,
        0xb9 : ShrInt2Addr,
        0xba : UshrInt2Addr,
        0xbb : AddLong2Addr,
        0xbc : SubLong2Addr,
        0xbd : MulLong2Addr,
        0xbe : DivLong2Addr,
        0xbf : RemLong2Addr,
        0xc0 : AndLong2Addr,
        0xc1 : OrLong2Addr,
        0xc2 : XorLong2Addr,
        0xc3 : ShlLong2Addr,
        0xc4 : ShrLong2Addr,
        0xc5 : UshrLong2Addr,
        0xc6 : AddFloat2Addr,
        0xc7 : SubFloat2Addr,
        0xc8 : MulFloat2Addr,
        0xc9 : DivFloat2Addr,
        0xca : RemFloat2Addr,
        0xcb : AddDouble2Addr,
        0xcc : SubDouble2Addr,
        0xcd : MulDouble2Addr,
        0xce : DivDouble2Addr,
        0xcf : RemDouble2Addr,
        0xd0 : AddIntLit16,
        0xd1 : SubIntLit16,
        0xd2 : MulIntLit16,
        0xd3 : DivIntLit16,
        0xd4 : RemIntLit16,
        0xd5 : AndIntLit16,
        0xd6 : OrIntLit16,
        0xd7 : XorIntLit16,
        0xd8 : AddIntLit8,
        0xd9 : SubIntLit8,
        0xda : MulIntLit8,
        0xdb : DivIntLit8,
        0xdc : RemIntLit8,
        0xdd : AndIntLit8,
        0xd3 : OrIntLit8,
        0xdf : XorIntLit8,
        0xe0 : ShlIntLit8,
        0xe1 : ShrIntLit8,
        0xe2 : UshrIntLit8,
        0xfa : InvokePolymorphic,       # Dex version >= 038
        0xfb : InvokePolymorphicRange,  # Dex version >= 038
        0xfc : InvokeCustom,            # Dex version >= 038
        0xfd : InvokeCustomRange,       # Dex version >= 038
        0xfe : ConstMethodHandle,       # Dex version >= 039
        0xff : ConstMethodType,         # Dex version >= 039
    }

    # Generate unused instruction handlers
    def _gen_unused(self):

        for i in range(0x3e, 0x44): self.instr[i] = Unused
        self.instr[0x73] = Unused
        for i in range(0x79, 0x7b): self.instr[i] = Unused
        for i in range(0xe3, 0xfa): self.instr[i] = Unused


    def __init__(self, bytecode, dex_version):

        # Only generate unused instruction handlers in debug mode
        if settings.DEBUG: self._gen_unused()

        self.dex_version = dex_version
        self.bytecode = bytecode
        self.insns = struct.unpack('H'*(len(self.bytecode)//2), self.bytecode)

    def __repr__(self):

        return str(self.insns)


if __name__ == '__main__':

    import sys

    settings.VERBOSE = True
    settings.DEBUG = True

    if len(sys.argv) < 2:
        error(sys.argv[0], '%s <Code file>' % (sys.argv[0]), fatal=True, pre='usage')

    code_file = sys.argv[1]
    code = CodeParser(dex_file)

