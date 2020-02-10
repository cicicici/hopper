from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from ..util.opt import Opt
from ..debug import dump

from enum import IntEnum
from enum import IntFlag


class DbgChn(IntFlag):
    NONE    = 0
    STD     = 1
    DEV     = 2
    DATA    = 4
    NET     = 8
    ALL     = 65535


class DbgLvl(IntEnum):
    NONE    = 0
    NOTSET  = 0
    MAX     = 5
    TRACE   = 5
    DEBUG   = 10
    MED     = 15
    INFO    = 20
    WARNING = 30
    MIN     = 35
    ERROR   = 40
    CRITICAL= 50


_dbg_cfg = Opt()
_dbg_cfg += Opt(level=DbgLvl.MAX, channel=DbgChn.ALL)

def dbg_cfg_val():
    global _dbg_cfg
    return _dbg_cfg

def dbg_cfg(**kwargs):
    global _dbg_cfg
    _dbg_cfg *= Opt(kwargs)
    if dbg_valid(DbgChn.STD, DbgLvl.MAX):
        dump.print_pp(_dbg_cfg)

def dbg_chn(channel):
    global _dbg_cfg
    return bool(_dbg_cfg.channel & channel)

def dbg_lvl(level):
    global _dbg_cfg
    return _dbg_cfg.level <= level

def dbg_valid(channel, level):
    return dbg_chn(channel) and dbg_lvl(level)

