#!/usr/bin/env python
# coding: utf-8
version = (0, 1, 2)

import sys, os
from setuptools import setup, find_packages

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

setup(
    name='msgpack-pure',
    version=version_str,
    packages=find_packages( exclude=["tests"] ),
    
    author='Keisuke Fukuda',
    author_email='keisukefukuda@gmail.com',
    license="Apache License 2",
    description = desc,
    long_description = long_desc,
    url='http://msgpack.org/',
    download_url='http://pypi.python.org/pypi/msgpack-pure/',
    classifiers=[
    'Programming Language :: Python :: 2',
    #'Programming Language :: Python :: 3',
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    ],
    
    test_suite="nose.collector"
    )

