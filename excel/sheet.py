from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import datetime
from copy import copy, deepcopy

from ..util.opt import Opt
from ..debug import log, dump

from .record import make_record, parse_fields
from .style import apply_style

def load_sheet(wb, sheetname, title_field_map, skip_empty=True, cache_size=100):
    if sheetname not in wb.sheetnames:
        return None

    ws = wb[sheetname]

    fields, fields_map = parse_fields(ws, title_field_map)
    log.trace(log.DC.STD, "== Loading [{}] ...".format(sheetname))
    if log.trace_on(log.DC.STD):
        dump.print_pp(fields)

    records = []

    # row 1 contains title names, not data
    row_cur = 1
    for i in range(2, ws.max_row+1):
        rec = make_record(fields, i)

        for f in fields:
            c = ws.cell(row=i, column=f.column)
            if c.value is not None:
                rec.empty = False
            rec[f.name].value = c.value
            rec[f.name].c_style = copy(c._style)

        #print(rec)
        #log.trace(log.DC.STD, "[{}] loc {}, b_shp {}, d_shp_out {}, d_act_sha {}".format(i, rec.a_location.value, rec.b_shp.value, rec.d_shp_out.value, rec.d_act_sha.value))
        if skip_empty and rec.empty:
            continue

        records.append(rec)
        row_cur += 1

    log.trace(log.DC.STD, "[{}] rows {}, columns {}, records {}".format(sheetname, ws.max_row, ws.max_column, len(records)))

    cache = Opt(size=cache_size, space=0)

    return Opt(wb=wb, ws=ws, name=sheetname, fields=fields, fields_map=fields_map, records=records, row=row_cur, cache=cache)

def append_sheet(sheet, rec, pre_style=True, post_style=True, data_format=True):
    if sheet.cache.space == 0:
        sheet.ws.insert_rows(sheet.row, sheet.cache.size)
        sheet.cache.space = sheet.cache.size

    fields = sheet.fields
    for f in fields:
        if f.name in rec:
            val = rec[f.name].value
            c = sheet.ws.cell(row=sheet.row, column=f.column)
            # Load template style, including data type and format
            if pre_style:
                c._style = copy(sheet.ws.cell(row=sheet.row+sheet.cache.space, column=f.column)._style)

            if data_format:
                #if type(val) is datetime.datetime:
                    #val = "{}/{}/{}".format(val.month, val.day, val.year)
                if f.dtype == 'date':
                    if val and isinstance(val, str):
                        #val = datetime.datetime.strptime(val, '%m/%d/%Y')
                        val = datetime.datetime.strptime(val, f.py_fmt)
                    c.number_format = f.dformat
                elif f.dtype == 'num':
                    if val is not None:
                        val = float(val)
                    c.number_format = f.dformat
                elif f.dtype == 'str':
                    if val is not None:
                        val = "{}".format(val)

            c.value = val

            # Apply additional style
            if post_style:
                apply_style(c, rec[f.name].style)

    sheet.row += 1
    sheet.cache.space -= 1

def append_found(sheet, sheet_save, found, mark_process=True, pre_style=True, post_style=True, data_format=True):
    for f in found:
        r = sheet.records[f]
        if r.processed:
            continue
        append_sheet(sheet_save, r, pre_style=pre_style, post_style=post_style, data_format=data_format)
        if mark_process:
            r.processed = True

def append_not_processed(sheet, sheet_save, first="*** INVALID ***", mark_process=True, pre_style=True, post_style=True, data_format=True):
    append_sheet(sheet_save, make_record(sheet_save.fields, 0, first=first), pre_style=pre_style, post_style=post_style, data_format=data_format)
    for r in sheet.records:
        if not r.processed:
            append_sheet(sheet_save, r, pre_style=pre_style, post_style=post_style, data_format=data_format)
            if mark_process:
                r.processed = True

def clear_sheet_cache(sheet):
    if sheet.cache.space > 0:
        sheet.ws.delete_rows(sheet.row, sheet.cache.space)

