from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import time
import sys
import argparse
import configparser
import json

from ..util.opt import Opt, dict_to_opt
from ..debug import log
from ..debug import dbg


class Config(object):

    def __init__(self, name="hopper", app='template', argv=None, command=None, unknown=False):
        self._name = name
        self._app = app
        if argv is None:
            self._argv = sys.argv[1:]
            self._command = sys.argv[0]
        else:
            self._argv = argv
            self._command = command
        self._unknown = unknown

        self.init_args()
        self.parse_args()
        self.default_config()
        self.init_config()
        if self.is_console():
            self.save_config()
        self.post_config()

    def is_console(self):
        return self._app and len(self._app) > 0

    def init_usr_args(self):
        pass

    def init_args(self):
        self.args_parser = argparse.ArgumentParser(
            description="Hopper {}".format(self._name),
            epilog="Usage: {} [-c config.ini] [options]".format(self._command)
        )

        self.init_usr_args()

        # optional arguments
        self.args_parser.add_argument('-c', type=str, action="store",
                                      help='Config file',
                                      default="config.ini")
        self.args_parser.add_argument('--tag', type=str, help='Tag')

        if self.is_console():
            self.args_parser.add_argument('--work_dir', type=str, help='Output dir')
            self.args_parser.add_argument('--inst_dir', type=str, help='Model dir')
            self.args_parser.add_argument('--add', type=str, help='Addtitional options')
            self.args_parser.add_argument('-m', type=str, help='Run mode')
            self.args_parser.add_argument('--trace', action='store_const', const=True, help='Enable tracing')

    def parse_args(self):
        if self._unknown:
            self._args, self._unknown_args = self.args_parser.parse_known_args(self._argv)
        else:
            self._args = self.args_parser.parse_args(self._argv)

    def default_set_config(self, section, key, val):
        self._default_config[section][key] = val

    def default_usr_config(self):
        pass

    def default_config(self):
        self._default_config = {}

        section = 'args'
        self._default_config[section] = {}
        # common configurations
        self._default_config[section]['name'] = self._name
        self._default_config[section]['tag'] = ""

        if self.is_console():
            self._default_config[section]['work_dir'] = "_work"
            self._default_config[section]['inst_dir'] = ""
            self._default_config[section]['add'] = {}
            self._default_config[section]['m'] = ""
            self._default_config[section]['trace'] = False

            # debug configurations
            section = 'debug'
            self._default_config[section] = {}
            self._default_config[section]['channel'] = log.DC.ALL
            self._default_config[section]['level'] = log.DL.DEBUG

        self.default_usr_config()

    def init_config(self):
        self._config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation())
        self._config.read(self._args.c)

        if 'args' not in self._config:
            self._config['args'] = {}
        if 'debug' not in self._config:
            self._config['debug'] = {}

        self._opt = Opt()

        # load config to opt
        for section in self._config.sections():
            opt = Opt()
            for key in self._config[section]:
                val_str =  self._config[section][key]
                val = json.loads(val_str)
                opt[key] = val
            self._opt[section] = opt

        # override with command line args
        for arg in vars(self._args):
            val = getattr(self._args, arg)
            if val is None:
                continue
            val_str = str(val)

            if arg in self._opt.args or arg in self._default_config['args']:
                if arg in self._opt.args:
                    opt_val = self._opt.args[arg]
                else:
                    opt_val = self._default_config['args'][arg]

                if isinstance(opt_val, str):
                    val_str = '"' + val_str + '"'

                if type(opt_val) is not type(val):
                    log.debug(log.DC.STD, "[Convert Arg] {}: {}, {} => {}".format(arg, val, type(val), type(opt_val)))
                    self._opt.args[arg] = json.loads(val_str)
                else:
                    self._opt.args[arg] = val
                self._config['args'][arg] = val_str
            else:
                self._opt.args[arg] = val
                self._config['args'][arg] = val_str

        # add default settings
        for section in self._default_config:
            opt = Opt()
            for key in self._default_config[section]:
                if key not in self._opt[section]:
                    opt[key] = self._default_config[section][key]
                    self._config[section][key] = json.dumps(opt[key])
            self._opt[section] += opt

        # additional post process
        if self._opt.args.add is not None and type(self._opt.args.add) is dict:
            self._opt.args.add = dict_to_opt(self._opt.args.add)

    def save_config(self):
        inst_dir = self._opt.args.inst_dir
        if not (inst_dir is not None and inst_dir.startswith('/')):
            if inst_dir is None or len(inst_dir) == 0:
                inst_dir=time.strftime('%Y%m%d_%H%M%S', time.localtime())
            if len(self._opt.args.tag) > 0:
                inst_dir = inst_dir + "_" + self._opt.args.tag
            inst_dir="{}/{}".format(self._opt.args.work_dir, inst_dir)

        try:
            if not os.path.isdir(inst_dir):
                os.makedirs(inst_dir)
        except:
            pass
        self._opt.args.inst_dir = inst_dir
        self._config['args']['_inst_dir'] = '"' + inst_dir + '"'
        # config file
        with open('{}/config.ini'.format(inst_dir), 'w') as configfile:
            self._config.write(configfile)

        # log file
        if self.is_console():
            log.set_log_file('{}/log.txt'.format(inst_dir))

        self._inst_dir = inst_dir

    def post_config(self):
        # Set debug settings
        if self.is_console():
            dbg.dbg_cfg(level=self._opt.debug.level,
                        channel=self._opt.debug.channel)

            if self._opt.args.trace and not dbg.dbg_lvl(log.DL.TRACE):
                dbg.dbg_cfg(level=log.DL.TRACE)

        # dump important information
        log.trace(log.DC.STD, "{} - {}".format(self._opt.args.name, self._opt.args.tag))
        log.trace(log.DC.STD, "  command [{}], argv {}".format(self._command, self._argv))
        log.trace(log.DC.STD, "  opt [{}]".format(self._opt))
        if self.is_console():
            log.trace(log.DC.STD, "  inst_dir [{}]".format(self._inst_dir))

    @property
    def opt(self):
        return self._opt;

    @property
    def command(self):
        return self._command;

