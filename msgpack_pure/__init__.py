# -*- coding: utf-8 -*-
from msgpack_pure._core import *
from msgpack_pure.__version__ import *

# compatible interfaces with simplejson/marshal/pickle.
load = unpack
loads = unpackb
dump = pack
dumps = packb
