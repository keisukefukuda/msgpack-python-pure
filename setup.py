#!/usr/bin/env python
# coding: utf-8
version = (0, 1, 0)

import sys, os
from glob import glob
from setuptools import setup

# make msgpack_pure/__verison__.py
f = open('msgpack_pure/__version__.py', 'w')
f.write("version = %r\n" % (version,))
f.close()
del f

version_str = '.'.join(map(str, version))

desc = 'MessagePack (de)serializer written in pure Python.'
long_desc = """MessagePack (de)serializer for Python.

What's MessagePack? (from http://msgpack.org/)

 MessagePack is a binary-based efficient data interchange format that is
 focused on high performance. It is like JSON, but very fast and small.
"""

setup(name='msgpack-pure',
      author='Keisuke Fukuda',
      author_email='keisukefukuda@gmail.com',
      license="Apache License 2",
      version=version_str,
      packages=['msgpack_pure'],
      description=desc,
      long_description=long_desc,
      url='http://msgpack.org/',
      download_url='http://pypi.python.org/pypi/msgpack-pure/',
      test_suite="nose.collector",
      classifiers=[
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          ]
      )

