from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from functools import cmp_to_key

from ..util.opt import Opt


def make_field(name, column, title, mapped, dtype, dformat, py_fmt):
    return Opt(name=name, column=column, title=title, mapped=mapped, dtype=dtype, dformat=dformat, py_fmt=py_fmt)

def make_cell(name, value, field, style=Opt()):
    return Opt(name=name, value=value, field=field, style=style, c_style=None)

def make_record(fields, row, first=None):
    rec = Opt()
    rec.row = row
    rec.valid = False
    rec.processed = False
    rec.first = None
    rec.empty = True
    rec.prop = Opt()

    for f in fields:
        rec[f.name] = make_cell(f.name, None, f)
        if rec.first is None:
            rec.first = rec[f.name]

    if first:
        rec.first.value = first

    return rec

def copy_record(r1, r2, fields, value=True, style=True, require_mapped=True):
    for f in fields:
        if require_mapped and not f.mapped:
            continue

        if f.name in r1:
            if value:
                r2[f.name].value = r1[f.name].value
            if style:
                r2[f.name].style = r1[f.name].style

def combine_record(r1, r2, fields, row=0, require_mapped=True):
    rec = make_record(fields, row)

    for f in fields:
        if require_mapped and not f.mapped:
            continue

        if f.name in r1:
            rec[f.name].value = r1[f.name].value
            rec[f.name].style = r1[f.name].style

        if f.name in r2:
            rec[f.name].value = r2[f.name].value
            rec[f.name].style = r2[f.name].style

    return rec

#cnt = Opt()
def parse_fields(sheet, title_field_map, title_row=1):
    #global cnt
    fields = []
    fields_map = Opt()

    for i in range(1, sheet.max_column+1):
        c = sheet.cell(row=title_row, column=i)
        #log.trace(log.DC.STD, "col {}, text: '{}'".format(i, c.value))
        #cnt.inc(c.value)

        if c.value in title_field_map:
            name = title_field_map[c.value]['name']
            mapped = True
            dtype = title_field_map[c.value]['type']
            dformat = title_field_map[c.value]['format']
            py_fmt = title_field_map[c.value]['py_fmt']
        elif c.value and c.value.startswith('_'):
            name = c.value
            mapped = False
            dtype = None
            dformat = None
            py_fmt = None
        else:
            name = "_{}".format(i)
            mapped = False
            dtype = None
            dformat = None
            py_fmt = None

        field = make_field(name, i, c.value, mapped, dtype, dformat, py_fmt)
        fields.append(field)
        fields_map[name] = field
    #dump.print_pp(cnt.to_dict())

    return (fields, fields_map)

def search_records_value(records, fields, needle, targets=[]):
    found = []
    for i, r in enumerate(records):
        if len(targets) > 0:
            for name in targets:
                if r[name].value == needle:
                    found.append(i)
        else:
            for f in fields:
                if r[f.name].value == needle:
                    found.append(i)
    return found

def search_records_multi(records, fields, targets=[], skip_value=[]):
    found = []

    for i, r in enumerate(records):
        match = True
        for f in targets:

            skip = False
            for sv in skip_value:
                if f.value == sv:
                    skip = True
                    break
            if skip:
                continue

            if r[f.name].value != f.value:
                match =False
                break

        if match:
            found.append(i)

    return found

def sort_records(records, fields=[]):
    def record_cmp(a, b):
        for f in fields:
            if a[f].value is None and b[f].value is None:
                continue
            elif a[f].value is None and b[f].value is not None:
                return -1
            elif a[f].value is not None and b[f].value is None:
                return 1
            elif a[f].value < b[f].value:
                return -1
            elif a[f].value > b[f].value:
                return 1
        return 0
    records.sort(key=cmp_to_key(record_cmp))

