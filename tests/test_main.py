#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct
import msgpack
import msgpack_pure

def _check(obj):
    # NOTE:
    # msgpack.packs(obj) nad msgpack_pure.packs(obj) are not necessarily
    # match because there are some possible variations which type to use
    # for integer values (i.e. uint8/int16 for 0xFF).
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

    for f in [0.0, 3.2342]:
        _check(f)

    _check_decode([0xa0 + 5, 1,2,3,4,5])
    _check_decode([0xda, 0, 5, ord('a'), ord('b'), ord('c'), ord('d'), ord('e')])
    _check_decode([0xdb, 0, 0, 0, 5, ord('a'), ord('b'), ord('c'), ord('d'), ord('e')])

    for s in ["test", "a" * 1000]:
        _check(s)

    _check( () )
    _check( (1, 1<<2, 1<<3, 1<<4, 1<<5, 1<<6, 1<<7) )
    _check( ("test", "test") )
    _check( (1, "2", 3, "4") )


