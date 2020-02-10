from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from functools import wraps
from contextlib import contextmanager

from .opt import Opt

__global_ctx_list = []

@contextmanager
def ctx(ctx_list, opt, **kwargs):
    global __global_ctx_list

    # append current context when enter
    if opt is None:
        _cur_ctx = Opt(kwargs)
    else:
        _cur_ctx = opt + Opt(kwargs)

    if ctx_list is None:
        __global_ctx_list += [_cur_ctx]
    else:
        ctx_list += [_cur_ctx]

    yield

    # clear current context when exit
    if ctx_list is None:
        del __global_ctx_list[-1]
    else:
        del ctx_list[-1]


def get_ctx_list(**kwargs):
    _cur_ctx = Opt(kwargs)
    return [_cur_ctx]


def get_ctx(ctx_list):
    global __global_ctx_list

    # merge current context
    res = Opt()
    if ctx_list is None:
        for c in reversed(__global_ctx_list):
            res += c
    else:
        for c in reversed(ctx_list):
            res += c

    return res


def dec_ctx_func(func):

    @wraps(func)
    def wrapper(ctx_list, **kwargs):
        # kwargs parsing
        _opt = Opt(kwargs) + get_ctx(ctx_list)

        _out = func(ctx_list, _opt)

        return _out

    return wrapper

