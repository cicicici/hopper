from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import sys
import random
import time


def timestamp_us(start=0):
    return int(round(time.time() * 1e6) - start)

def timestamp_ms(start=0):
    return int(round(time.time() * 1e3) - start)

def token_in_list(line_list, token):
    in_list = False

    if line_list and len(token) > 0:
        for line in line_list:
            if token in line:
                in_list = True
                break

    return in_list

def list_in_token(line_list, token):
    in_token = False

    if line_list and len(token) > 0:
        for line in line_list:
            if line in token:
                in_token = True
                break

    return in_token

def split_list(line_list, parts, rand=False):
    splits = None

    if line_list and parts > 0:
        splits = []
        for i in range(parts):
            splits.append([])

        if rand:
            random.shuffle(line_list)

        for i, line in enumerate(line_list):
            splits[i%parts].append(line)

    return splits

def contains_any_chars(string, char_set):
    for c in char_set:
        if c in string: return True
    return False

def contains_all_chars(string, char_set):
    for c in char_set:
        if c not in string: return False
    return True

