from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import json
import base64


def opt_to_dict(opt):
    d = {}
    for k, v in opt.items():
        if type(v) is Opt:
            d[k] = opt_to_dict(v)
        elif type(v) is bytes:
            b64_b = base64.b64encode(v)
            b64_v = b64_b.decode('ascii')
            d[k] = {'_b64_v': b64_v, '_len': len(v)}
        else:
            d[k] = v
    return d

def dict_to_opt(d):
    opt = Opt()
    for k, v in d.items():
        if type(v) is dict:
            if '_b64_v' in v:
                b64_b = v['_b64_v'].encode('ascii')
                data_b = base64.b64decode(b64_b)
                opt[k] = data_b
            else:
                opt[k] = dict_to_opt(v)
        else:
            opt[k] = v
    return opt

def opt_to_file(opt, fname):
    with open(fname, 'w') as f:
        json.dump(opt_to_dict(opt), f, indent=2)

def opt_from_file(fname):
    with open(fname, 'r') as f:
        return dict_to_opt(json.load(f))

class Opt(collections.MutableMapping):

    def __init__(self, *args, **kwargs):
        self.__dict__.update(*args, **kwargs)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, key):
        return self.__dict__[key]

    def __delitem__(self, key):
        del self.__dict__[key]

    # Fallback for missing attributes
    def __getattr__(self, key):
        return None

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__dict__.__repr__()

    def __add__(self, other):
        res = Opt(self.__dict__)
        for k, v in other.items():
            #if k not in res.__dict__ or res.__dict__[k] is None:
            if k not in res.__dict__:
                res.__dict__[k] = v
        return res

    def __mul__(self, other):
        res = Opt(self.__dict__)
        for k, v in other.items():
            res.__dict__[k] = v
        return res

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # in-place add/mul instead of return a new one like ops above
    def set(self, key, value, overwrite=False):
        if key is not None and (overwrite or (key not in self.__dict__)):
            self.__dict__[key] = value
            return self
        return None

    # counter functions
    def inc(self, key, delta=1):
        if key is None:
            return
        if key not in self.__dict__:
            self.__dict__[key] = delta
        else:
            self.__dict__[key] += delta

    def dec(self, key, delta=1):
        if key is None:
            return
        if key not in self.__dict__:
            self.__dict__[key] = -delta
        else:
            self.__dict__[key] -= delta

    def clr(self, key, val=0):
        if key is None:
            return
        self.__dict__[key] = val

    def to_dict(self):
        return opt_to_dict(self)

    @staticmethod
    def from_dict(d):
        return dict_to_opt(d)

    def dumps(self):
        return json.dumps(opt_to_dict(self))

    def loads(self, s):
        res = Opt(self.__dict__)
        res *= dict_to_opt(json.loads(s))
        return res

    def to_file(self, fname):
        opt_to_file(self, fname)

    @staticmethod
    def from_file(fname):
        return opt_from_file(fname)

