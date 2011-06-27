# -*- coding: utf-8 -*-

import struct

# Object headers
_NIL = 0xc0
_TRUE = 0xc3
_FALSE = 0xc2

_UINT8  = 0xcc
_UINT16 = 0xcd
_UINT32 = 0xce
_UINT64 = 0xcf
_INT8   = 0xd0
_INT16  = 0xd1
_INT32  = 0xd2
_INT64  = 0xd3

_FLOAT  = 0xca
_DOUBLE = 0xcb

_FIX_RAW = 0xa0
_RAW16   = 0xda
_RAW32   = 0xdb

_FIX_ARY = 0x90
_ARY16   = 0xdc
_ARY32   = 0xdd

_FIX_MAP = 0x80
_MAP16   = 0xde
_MAP32   = 0xdf


# Constants
_INT8_MAX   = 0x7F
_INT8_MIN   = -_INT8_MAX - 1
_INT16_MAX  = 0x7FFF
_INT16_MIN  = -_INT16_MAX - 1
_INT32_MAX  = 0x7FFFFFFF
_INT32_MIN  = -_INT32_MAX - 1
_INT64_MAX  = 0x7FFFFFFFFFFFFFFF
_INT64_MIN  = -_INT64_MAX - 1

_UINT8_MAX  = 0xFF
_UINT16_MAX = 0xFFFF
_UINT32_MAX = 0xFFFFFFFF
_UINT64_MAX = 0xFFFFFFFFFFFFFFFF

def packs(obj, **kwargs):
    if kwargs.get('default'):
        obj = kwargs['default'](obj)

    if obj == None:  return chr(_NIL)

    if isinstance(obj,bool) and obj:
        return chr(_TRUE)

    if isinstance(obj,bool) and obj == False:
        return chr(_FALSE)

    if isinstance(obj, int) or isinstance(obj, long):
        # Positive Fixnum
        if 0 <= obj and obj <= 127:
            return struct.pack("B", obj)

        # Negative Fixnum
        elif -32 <= obj and obj <= 0:
            return struct.pack("b", obj)

        # uint 8
        elif 0 <= obj <= _UINT8_MAX:
            return struct.pack("BB", _UINT8, obj)

        # int 8
        elif _INT8_MIN <= obj and obj <= _INT8_MAX:
            return struct.pack(">Bb", _INT8, obj)

        # uint 16
        elif 0 <= obj <= _UINT16_MAX:
            return struct.pack(">BH", _UINT16, obj)

        elif _INT16_MIN <= obj and obj <= _INT16_MAX:
            return struct.pack(">Bh", _INT16, obj)

        # int 32
        elif _INT32_MIN <= obj and obj <= _INT32_MAX:
            return struct.pack(">Bi", _INT32, obj)

        # uint 32
        elif 0 <= obj <= _UINT32_MAX:
            return struct.pack(">BI", _UINT32, obj)

        # int 64
        elif _INT64_MIN <= obj and obj <= _INT64_MAX:
            return struct.pack(">Bq", _INT64, obj)

        # uint64
        elif 0 <= obj <= _UINT64_MAX:
            return struct.pack(">BQ", _UINT64, obj)

        raise RuntimeError, "Integer value out of range"

    # raw bytes
    if isinstance(obj, str) or isinstance(obj, unicode):
        if isinstance(obj, unicode):
            obj = obj.encode('utf-8')
        nbytes = len(obj)
        if nbytes <= 31:
            mark = chr(_FIX_RAW + nbytes)
            obj = mark + obj
            return struct.pack("%ds" % len(obj), obj)

        elif nbytes <= 2**16-1:
            return struct.pack(">BH%ds" % nbytes, _RAW16, nbytes, obj)

        elif nbytes <= 2**32-1:
            return struct.pack(">BI%ds" % nbytes, _RAW32, nbytes, obj)

    # float
    if isinstance(obj, float):
        return struct.pack(">Bd", _DOUBLE, obj)

    # array
    if isinstance(obj, list) or isinstance(obj, tuple):
        packed = ""
        sz = len(obj)

        if sz <= 15:
            packed += chr(_FIX_ARY + (sz & 0x0f))
            for i in range(sz):
                packed += packs(obj[i], **kwargs)

        elif sz <= 2**16-1:
            packed += chr(_ARY16)
            packed += struct.pack(">H", sz)
            for i in range(sz):
                packed += packs(obj[i], **kwargs)

        elif sz <= 2**32-1:
            packed += chr(_ARY32)
            packed += struct.pack(">I", sz)
            for i in range(sz):
                packed += packs(obj[i], **kwargs)

        return packed

    # map
    if isinstance(obj, dict):
        sz = len(obj)
        packed = ""
        if sz <= 15:
            packed += chr(_FIX_MAP + sz)
        elif sz <= 2**16-1:
            packed += struct.pack(">BH", _MAP16, sz)
        elif sz <= 2**32-1:
            packed += struct.pack(">BI", _MAP32, sz)

        for (k,v) in obj.iteritems():
            packed += packs(k, **kwargs)
            packed += packs(v, **kwargs)

        return packed

    # otherwise: unknown type
    raise TypeError

def _apply_hook(obj, **kwargs):
    obj_hook = kwargs.get('object_hook')
    ary_hook = kwargs.get('list_hook')
    default  = kwargs.get('default')

    if ary_hook and (isinstance(obj, list) or isinstance(obj, tuple)):
        if not callable(ary_hook):
            raise Type("list_hook must be a callable.")
        obj = ary_hook(obj)

    elif obj_hook and isinstance(obj, dict):
        if not callable(obj_hook):
            raise TypeError("object_hook must be a callable.")
        obj = obj_hook(obj)

    elif default:
        if not callable(default):
            raise TypeError("default must be a callable.")
        obj = default(obj)

    return obj
    

def read_obj(packed, **kwargs):
    if packed is None or len(packed) == 0: return None,0
    b = ord(packed[0])
    packed = packed[1:]
    consumed = 1 # b's 1 byte

    obj_hook = kwargs.get('object_hook')
    ary_hook = kwargs.get('list_hook')
    default  = kwargs.get('default')

    # Positive Fixnum
    if b & (1 << 7) == 0:
        obj = b

    # Negative Fixnum
    elif b & 0xE0 == 0xE0:
        obj, = struct.unpack("b", chr(b))

    elif b == _UINT8:
        # TODO: error check
        obj, = struct.unpack("B", packed[0])
        consumed += 1

    elif b == _INT8:
        obj, = struct.unpack("b", packed[:1])
        consumed += 1

    elif b == _UINT16:
        # TODO: error check
        obj, = struct.unpack(">H", packed[:2])
        consumed += 2

    elif b == _INT16:
        # TODO: error check
        obj, = struct.unpack(">h", packed[:2])
        consumed += 2

    elif b == _UINT32:
        # TODO: error check
        obj, = struct.unpack(">I", packed[:4])
        consumed += 4

    elif b == _INT32:
        # TODO: error check
        obj, = struct.unpack(">i", packed[:4])
        consumed += 4

    elif b == _UINT64:
        # TODO: error check
        # I'm not sure that format 'Q' is always available...
        obj, = struct.unpack(">Q", packed[:8])
        consumed += 8

    elif b == _INT64:
        # TODO: error check
        obj, = struct.unpack(">q", packed[:8])
        consumed += 8

    elif b == _FLOAT:
        obj, = struct.unpack(">f", packed[:4])
        consumed += 4

    elif b == _DOUBLE:
        obj, = struct.unpack(">d", packed[:8])
        consumed += 8

    elif b == _NIL:   obj = None
    elif b == _TRUE:  obj = True
    elif b == _FALSE: obj = False

    elif (b & 0xe0) == _FIX_RAW:
        nbytes = b & 0x1F
        obj, = struct.unpack("%ds" % nbytes, packed[:nbytes])
        consumed += nbytes

    elif b == _RAW16:
        nbytes, = struct.unpack(">H", packed[:2])
        packed = packed[2:]
        obj, = struct.unpack("%ds" % nbytes, packed[:nbytes])
        consumed += nbytes + 2

    elif b == _RAW32:
        nbytes, = struct.unpack(">I", packed[:4])
        packed = packed[4:]
        obj, = struct.unpack("%ds" % nbytes, packed[:nbytes])
        consumed += nbytes + 4

    elif (b & 0xF0) == _FIX_ARY:
        sz = b & 0x0F
        obj,c = _read_list_body(packed, sz, **kwargs)
        consumed += c

    elif b == _ARY16:
        sz, = struct.unpack(">H", packed[:2])
        consumed += 2
        packed = packed[2:]

        obj,c = _read_list_body(packed, sz, **kwargs)
        consumed += c

    elif b == _ARY32:
        sz, = struct.unpack(">I", packed[:4])
        consumed += 4
        packed = packed[4:]

        obj,c = _read_list_body(packed, sz, **kwargs)
        consumed += c

    elif (b & 0xF0) == _FIX_MAP:
        sz = b & 0x0F
        obj,c = _read_map_body(packed, sz, **kwargs)
        consumed += c

    elif b == _MAP16:
        sz, = struct.unpack(">H", packed[:2])
        consumed += 2
        packed = packed[2:]

        obj,c = _read_map_body(packed, sz, **kwargs)
        consumed += c

    elif b == _MAP32:
        sz, = struct.unpack(">I", packed[:4])
        consumed += 4
        packed = packed[4:]

        obj, c = _read_map_body(packed, sz, **kwargs)
        consumed += c

    else:
        raise RuntimeError, "Unknown object header: 0x%x" % b

    return _apply_hook(obj, **kwargs), consumed


def _read_list_body(packed, sz, **kwargs):
    obj = ()
    consumed = 0
    for i in range(sz):
        o,c = read_obj(packed)
        o = _apply_hook(o, **kwargs)
        obj = obj + (o,)
        packed = packed[c:]
        consumed += c

    return _apply_hook(obj, **kwargs), consumed

def _read_map_body(packed, sz, **kwargs):
    obj_hook = kwargs.get('object_hook')
    ary_hook = kwargs.get('list_hook')
    default  = kwargs.get('default')

    obj = {}
    consumed = 0

    for i in range(sz):
        k,c = read_obj(packed)
        consumed += c
        packed = packed[c:]

        v,c = read_obj(packed)
        consumed += c
        packed = packed[c:]

        k = _apply_hook(k, **kwargs)
        v = _apply_hook(v, **kwargs)

        obj[k] = v

    return _apply_hook(obj, **kwargs), consumed


def unpacks(packed, **kwargs):
    if packed is None or len(packed) == 0: return None

    obj, consumed = read_obj(packed, **kwargs)

    return obj

unpack = unpackb = unpacks
pack = packb = packs
