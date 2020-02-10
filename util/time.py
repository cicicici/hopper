from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import time

def time_now():
    return time.time()

def time_str(tm):
    tm_tuple = time.localtime(tm)
    tm_ms = int(1e6 * (tm % 1.0))

    s = '%04d/%02d/%02d %02d:%02d:%02d.%06d' % (
            tm_tuple[0],  # year
            tm_tuple[1],  # month
            tm_tuple[2],  # day
            tm_tuple[3],  # hour
            tm_tuple[4],  # min
            tm_tuple[5],  # sec
            tm_ms)
    return s

