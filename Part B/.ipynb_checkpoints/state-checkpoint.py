import sys
import json
import math
import typing
import itertools
import collections

HEX_RANGE = range(-4, +4+1)
ALL_HEXES = frozenset(
        Hex(r, q) for r in HEX_RANGE for q in HEX_RANGE if -r-q in HEX_RANGE
    )
HEX_STEPS = [Hex(r, q) for r, q in [(1,-1),(1,0),(0,1),(-1,1),(-1,0),(0,-1)]]


BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

class RoPaSci360:
    def __init__(self)
    