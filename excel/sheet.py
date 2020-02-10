from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import datetime
from copy import copy, deepcopy

from ..util.opt import Opt, opt_to_dict, opt_to_file
from ..debug import log, dump

from .record import make_record, parse_fields
from .style import apply_style

def load_sheet(wb, sheetname, title_field_map, skip_empty=True):
    if sheetname not in wb.sheetnames:
        return None

    ws = wb[sheetname]

    fields, fields_map = parse_fields(ws, title_field_map)
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

        #print(rec)
        #log.trace(log.DC.STD, "[{}] loc {}, b_shp {}, d_shp_out {}, d_act_sha {}".format(i, rec.a_location.value, rec.b_shp.value, rec.d_shp_out.value, rec.d_act_sha.value))
        if skip_empty and rec.empty:
            continue

        records.append(rec)
        row_cur += 1

    log.trace(log.DC.STD, "[{}] rows {}, columns {}, records {}".format(sheetname, ws.max_row, ws.max_column, len(records)))

    return Opt(wb=wb, ws=ws, name=sheetname, fields=fields, fields_map=fields_map, records=records, row=row_cur)

def append_sheet(sheet, rec):
    sheet.ws.insert_rows(sheet.row, 1)

    fields = sheet.fields
    for f in fields:
        if f.name in rec:
            val = rec[f.name].value
            if type(val) is datetime.datetime:
                val = "{}/{}/{}".format(val.month, val.day, val.year)
            c = sheet.ws.cell(row=sheet.row, column=f.column)
            c.value = val
            c._style = copy(sheet.ws.cell(row=sheet.row+1, column=f.column)._style)

            apply_style(c, rec[f.name].style)

    sheet.row += 1

def append_found(sheet, sheet_save, found, mark_process=True):
    for f in found:
        r = sheet.records[f]
        if r.processed:
            continue
        append_sheet(sheet_save, r)
        if mark_process:
            r.processed = True

def append_not_processed(sheet, sheet_save, first="*** INVALID ***", mark_process=True):
    append_sheet(sheet_save, make_record(sheet_save.fields, 0, first=first))
    for r in sheet.records:
        if not r.processed:
            append_sheet(sheet_save, r)
            if mark_process:
                r.processed = True

