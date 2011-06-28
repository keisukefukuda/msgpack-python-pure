# -*- coding: utf-8 -*-

import struct
import mmap

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

        raise RuntimeError("Integer value out of range")

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
    raise TypeError()


class Unpacker():
    def __init__(self, **kwargs):
        self.default_hook = kwargs.get('default')
        self.object_hook  = kwargs.get('object_hook')
        self.list_hook    = kwargs.get('list_hook')

        if self.list_hook and not callable(self.list_hook):
            raise TypeError("list_hook must be a callable.")
        
        if self.object_hook and not callable(self.object_hook):
            raise TypeError("object_hook must be a callable.")
        
        if self.default_hook and not callable(self.default_hook):
            raise TypeError("default_hook must be a callable.")
            

    def apply_hook(self, obj, **kwargs):
        if self.list_hook and (isinstance(obj, list) or isinstance(obj, tuple)):
            obj = self.list_hook(obj)

        elif self.object_hook and isinstance(obj, dict):
            obj = self.object_hook(obj)

        elif self.default_hook:
            obj = self.default_hook(obj)

        return obj

    def unpacks(self, packed):
        if packed is None or len(packed) == 0: return None

        mp = mmap.mmap(-1, len(packed))
        mp.write(packed)
        mp.seek(0)

        obj = self.read_obj(mp)

        return obj

    def read_obj(self, mp):
        try:
            b = ord(mp.read_byte())
        except ValueError,e:
            return None

        # Positive Fixnum
        if b & (1 << 7) == 0:
            obj = b

            # Negative Fixnum
        elif b & 0xE0 == 0xE0:
            obj = struct.unpack("b", chr(b))[0]

        elif b == _UINT8:
            obj = struct.unpack("B", mp.read_byte())[0]

        elif b == _INT8:
            obj = struct.unpack("b", mp.read_byte())[0]

        elif b == _UINT16:
            obj = struct.unpack(">H", mp.read(2))[0]

        elif b == _INT16:
            obj = struct.unpack(">h", mp.read(2))[0]

        elif b == _UINT32:
            obj = struct.unpack(">I", mp.read(4))[0]

        elif b == _INT32:
            obj = struct.unpack(">i", mp.read(4))[0]

        elif b == _UINT64:
            # I'm not sure that format 'Q' is always available...
            obj = struct.unpack(">Q", mp.read(8))[0]

        elif b == _INT64:
            obj = struct.unpack(">q", mp.read(8))[0]

        elif b == _FLOAT:
            obj = struct.unpack(">f", mp.read(4))[0]

        elif b == _DOUBLE:
            obj = struct.unpack(">d", mp.read(8))[0]

        elif b == _NIL:   obj = None
        elif b == _TRUE:  obj = True
        elif b == _FALSE: obj = False

        elif (b & 0xe0) == _FIX_RAW:
            nbytes = b & 0x1F
            obj = struct.unpack("%ds" % nbytes, mp.read(nbytes))[0]

        elif b == _RAW16:
            nbytes, = struct.unpack(">H", mp.read(2))
            obj = struct.unpack("%ds" % nbytes, mp.read(nbytes))[0]

        elif b == _RAW32:
            nbytes = struct.unpack(">I", mp.read(4))[0]
            obj = struct.unpack("%ds" % nbytes, mp.read(nbytes))[0]

        elif (b & 0xF0) == _FIX_ARY:
            sz = b & 0x0F
            obj = self.read_list_body(mp, sz)

        elif b == _ARY16:
            sz = struct.unpack(">H", mp.read(2))[0]
            obj = self.read_list_body(mp, sz)

        elif b == _ARY32:
            sz = struct.unpack(">I", mp.read(4))[0]
            obj = self.read_list_body(mp, sz)

        elif (b & 0xF0) == _FIX_MAP:
            sz = b & 0x0F
            obj = self.read_map_body(mp, sz)

        elif b == _MAP16:
            sz = struct.unpack(">H", mp.read(2))[0]
            obj = self.read_map_body(mp, sz)

        elif b == _MAP32:
            sz = struct.unpack(">I", mp.read(4))[0]
            obj = self.read_map_body(mp, sz)

        else:
            raise RuntimeError("Unknown object header: 0x%x" % b)

        return self.apply_hook(obj)


    def read_list_body(self, mp, sz):
        obj = []
        for i in range(sz):
            o = self.read_obj(mp)
            o = self.apply_hook(o)
            obj.append(o)
            
        obj = tuple(obj)
        return self.apply_hook(obj)

    def read_map_body(self, mp, sz):
        obj = {}

        for i in range(sz):
            k = self.read_obj(mp)
            v = self.read_obj(mp)

            k = self.apply_hook(k)
            v = self.apply_hook(v)

            obj[k] = v

        return self.apply_hook(obj)
    
def unpacks(packed, **kwargs):
    return Unpacker(**kwargs).unpacks(packed)

unpack = unpackb = unpacks
pack = packb = packs
