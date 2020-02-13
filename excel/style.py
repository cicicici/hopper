from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys

from openpyxl.styles import PatternFill, Border, Side, Alignment, Protection, Font, colors, Color, GradientFill


class ColorPalette():
    WHITE       = 'FFFFFF'
    BLACK       = '010101'
    RED         = 'EA9999'
    DARK_RED    = 'FE0101'
    GREEN       = 'C7E0B4'
    DARK_GREEN  = '00B04F'
    BLUE        = 'B4C6E8'
    DARK_BLUE   = '06AFF0'
    YELLOW      = 'FFFF01'
    DARK_YELLOW = 'FFBF01'
    GREY        = 'AAAAAA'
    DARK_GREY   = '808080'
    AQUA        = '01FFFF'
    BISQUE      = 'FFE4C4'
    ROYBLUE     = '4169E1'
    VIOLET      = 'EE82EE'
    LIGHTPINK   = 'FFB6C2'
    HOTPINK     = 'FE69B4'

HighLightColorBoard = [
    ColorPalette.YELLOW,
    ColorPalette.AQUA,
    ColorPalette.BISQUE,
    ColorPalette.ROYBLUE,
    ColorPalette.VIOLET,
    ColorPalette.LIGHTPINK,
    ColorPalette.GREEN,
    ColorPalette.RED,
    ColorPalette.BLUE,
    ColorPalette.GREY,
    ColorPalette.HOTPINK,
    ColorPalette.DARK_YELLOW,
    ColorPalette.DARK_GREEN,
    ColorPalette.DARK_RED,
    ColorPalette.DARK_BLUE,
    ColorPalette.DARK_GREY]

def apply_style(cell, style):
    if not style:
        return

    if style.highlight:
        cell.fill = GradientFill(stop=(style.highlight, style.highlight))

    if style.border:
        #edge = Side(border_style="thin", color=style.border.color)
        edge = Side(border_style=style.border.style, color=style.border.color)
        cell.border = Border(top=edge, left=edge, right=edge, bottom=edge)

    if style.font:
        cell.font = style.font

    if style.alignment:
        cell.alignment = style.alignment

