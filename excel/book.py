from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import datetime

from copy import copy, deepcopy
from openpyxl import load_workbook

from ..util.opt import Opt, opt_to_dict, opt_to_file
from ..debug import log, dump

from .sheet import load_sheet


def load_book(filename, title_sheet_map, title_field_map):
    wb = load_workbook(filename)
    log.trace(log.DC.STD, "Book: {}, sheets {}".format(filename, wb.sheetnames))

    sheets = Opt()

    for sheetname in wb.sheetnames:
        if sheetname in title_sheet_map:
            name = title_sheet_map[sheetname]
        else:
            name = sheetname

        sheets[name] = load_sheet(wb, sheetname, title_field_map)

    return Opt(wb=wb, sheets=sheets)
