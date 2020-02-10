from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

import hashlib

BLOCK_SIZE=1024 * 512

def md5_str(s):
    return hashlib.md5(s.encode('utf-8')).hexdigest()

def md5_file(fname):
    m = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(BLOCK_SIZE), b""):
            m.update(chunk)
    return m.hexdigest()

