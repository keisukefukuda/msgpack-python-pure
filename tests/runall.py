#!/bin/env/python
# -*- coding: utf-8 -*-
import sys

from os.path import join,dirname
sys.path.append(join(dirname(sys.argv[0]), '..'))
print join(dirname(sys.argv[0]), '..')

from test_case import *
from tests.test_except import *
from tests.test_main import *

if __name__ == '__main__':
    import nose
    nose.main()

