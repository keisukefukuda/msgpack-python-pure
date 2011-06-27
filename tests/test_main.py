#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys,os.path
sys.path = [os.path.join(os.path.dirname(sys.argv[0]),'..')] + sys.path

import struct
import msgpack
import msgpack_pure

def _list_to_tuple(obj):
    if isinstance(obj, list):
        return tuple( map(_list_to_tuple, obj) )
    else:
        return obj

def _check(obj):
    # NOTE:
    # msgpack.packs(obj) nad msgpack_pure.packs(obj) are not necessarily
    # match because there are some possible variations which type to use
    # for integer values (i.e. uint8/int16 for 0xFF).
    obj = _list_to_tuple(obj)
    
    assert msgpack_pure.unpacks(msgpack.packs(obj)) == obj
    assert msgpack.unpacks(msgpack_pure.packs(obj)) == obj
    assert msgpack_pure.unpacks(msgpack_pure.packs(obj)) == obj

def _check_decode(bytes):
    packed = struct.pack("B" * len(bytes), *bytes)
    assert msgpack.unpacks(packed) == msgpack_pure.unpacks(packed)

def test_int():
    ### For format specification,
    ### see http://wiki.msgpack.org/display/MSGPACK/Format+specification
    
    # positive fixnum / uint 8 / uint 16
    for i in [1, 1<<2, 1<<3, 1<<4, 1<<5, 1<<6, 1<<7, 1<<8, 1<<9, 1<<10]:
        _check(i)

    for i in [0x7F, 0xFF, 0x7FFF, 0xFFFF, 0x7FFFFFFF, 0xFFFFFFFF,
              0x7FFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF]:
        _check(i)

    for i in [-0x7F-1, -0x7FFF-1, -0x7FFFFFFF-1, -0x7FFFFFFFFFFFFFFF-1]:
        _check(i)

    # negative fixnum
    for i in [-1, -32]:
        _check(i)

    for b in [None, True, False]:
        _check(b)

def test_float():
    for f in [0.0, 3.2342]:
        _check(f)

def test_raw():
    _check_decode([0xa0 + 5, 1,2,3,4,5])
    _check_decode([0xda, 0, 5, ord('a'), ord('b'), ord('c'), ord('d'), ord('e')])
    _check_decode([0xdb, 0, 0, 0, 5, ord('a'), ord('b'), ord('c'), ord('d'), ord('e')])
    
def test_array():
    for s in ["test", "a" * 1000]:
        _check(s)

    _check( () )
    _check( [] )
    _check( [1, 1<<2, 1<<3, 1<<4, 1<<5, 1<<6, 1<<7] )
    _check( ("test", "test") )
    _check( (1, "2", 3, "4") )

    # ary 16
    _check_decode( [0xdc, 0x00, 0x01, 1] )

    # ary 32
    _check_decode( [0xdd, 0x00, 0x00, 0x00, 0x02, 1, 2] )

def test_nested_array():
    _check( ((),) )

def test_map():
    _check( {} )
    _check( {1:2} )
    _check( {1 : "foo", "bar" : 999999} )

    # map 16
    _check_decode( [0xde, 0x00, 0x01, 1, 1] )

    # map 32
    _check_decode( [0xdf, 0x00, 0x00, 0x00, 0x02, 1,1, 2,2] )

def test_nested_array():
    _check( {1 : {2 : 3}, 4 : {5 : 6} } )


if __name__ == "__main__":
    import nose
    nose.main()
