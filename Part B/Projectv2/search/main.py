"""
COMP30024 Artificial Intelligence, Semester 1, 2021
Project Part A: Searching

This script contains the entry point to the program (the code in
`__main__.py` calls `main()`). Your solution starts here!
"""

import sys
import json
import numpy as np
import math

# If you want to separate your code into separate files, put them
# inside the `search` directory (like this one and `util.py`) and
# then import from them like this:
from search.util import print_board, print_slide, print_swing
from search.classes import *

##******************************** FUNCTIONS ********************************##

def input_to_board(data):
    board_dict = {}
    for key, value in data.items():
        for n in value:
            if key == 'upper':
                board_dict[(n[1], n[2])] = n[0].upper()
            elif key == 'lower':
                board_dict[(n[1], n[2])] = n[0]
            elif key == 'block':
                board_dict[(n[1], n[2])] = "O"
    return board_dict

##***************************************************************************##
## This function is to calculate the distance between the start and the final
## point, where Position 1 is the initial point and Position 2 is the
## goal point.
## Implemented from (redblobgames.com/grids/hexagons/#distances).
def hex_distance(pos1, pos2):
    return (abs(pos1[1][1] - pos2[1][1])
        + abs(pos1[1][1] + pos1[1][0] - pos2[1][1] - pos2[1][0])
        + abs(pos1[1][0] - pos2[1][0])) / 2

def a_star(initial_state): pass

##********************************** MAIN ***********************************##

def main():
    try:
        with open(sys.argv[1]) as file:
            data = json.load(file)
    except IndexError:
        print("usage: python3 -m search path/to/input.json", file=sys.stderr)
        sys.exit(1)

    board_dict = input_to_board(data)
    print_board(board_dict,"THE BOARD",ansi=True)

    upper = frozenset(map(tuple, data['upper']))
    lower = frozenset(map(tuple, data['lower']))
    blocks = list(map(tuple, data['block']))

    rps = RoPaSci360(9, 9, blocks)
    initial_state = state(upper, lower, rps)
    print(initial_state._actions())
