# msgpack-python-pure

 This is a pure-Python implementation of
msgpack-puthon(http://pypi.python.org/pypi/msgpack-python/) by INADA
Naoki.  It is intended to be perfectly compatible with
msgpack-python. Most of the unitests are borrowed from msgpack-python
with a few exceptions that depend on its internal structure.

As it is written in pure Python, it can work on a platform where
native extensions are not allowed, such as Google App Engine.

# Usage

Usage is just as the same as msgpack-python. Just change the import line.

  from msgpack_pure import packs, unpacks

# Perforamnce

As written in pure Python, its performance is much lower than the
native extension. It is slower by 10-50 times than msgpack-python.
You are recommended to use msgpack-python whereever it is available.
