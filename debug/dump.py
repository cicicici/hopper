from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


import pprint
pp = pprint.PrettyPrinter(indent=4)


def print_pp(obj, name="Obj"):
    global pp
    pp.pprint(obj)

