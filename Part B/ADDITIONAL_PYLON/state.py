import sys
import json
import math
import typing
import itertools
import collections

from copy import deepcopy

#HEX_RANGE = range(-4, +4+1)
# Create the board and all legal coordinates for RoPaSci360
#ALL_HEXES = frozenset(
#        Hex(r, q) for r in HEX_RANGE for q in HEX_RANGE if -r-q in HEX_RANGE
#    )
#HEX_STEPS = [Hex(r, q) for r, q in [(1,-1),(1,0),(0,1),(-1,1),(-1,0),(0,-1)]] # Neighbours of the current pieces.

BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}
SYMBOLS = ('r', 's', 'p')
MAX_TURNS = 360
MAX_SAME_CONFIG = 3
NO_OF_TOKEN = 9

UPPER_BOUND = +4
LOWER_BOUND = -4

BOUNDS = range(LOWER_BOUND, UPPER_BOUND+1)
grid = [(r, q) for r in BOUNDS for q in BOUNDS if -r-q in BOUNDS]

GAME_STATES = {}

class RoPaSci360:
    def __init__(self, player = 'upper'):
        self.upper = list()
        self.lower = list()

        self.upper_throws = 9
        self.lower_throws = 9

        self.turn = 0
        self.game_state = 'running'
        self.condition = None
        self.done = False

        self.upper_inv = False
        self.lower_inv = False

        self.player_1 = player
        self.player_2 = self.get_other_player()

    def inbound(self, location):
        (r, q) = location
        if abs(r) > UPPER_BOUND or abs(q) > UPPER_BOUND:
            return False

        list = [(4, 1), (4, 2), (4, 3), (4, 4), (3, 2),
                (3, 3), (3, 4), (2, 3), (2, 4), (1, 4),
                (-1, -4), (-2, -4), (-2, -3), (-3, -4), (-3, -3),
                (-3, -2), (-4, -4), (-4, -3), (-4, -2), (-4, -1)]

        return location not in list

    def neighbours(self, location):
        (r, q) = location
        ## Neighbours in order of Top-Left, Top-Right, Mid-Left, Mid-Right,
        ## Bottom-Left, Bottom-Right
        neighbours = [(r + 1, q - 1), (r + 1, q),
                      (r, q - 1), (r, q + 1),
                      (r - 1, q), (r - 1, q + 1)]

        results = filter(self.inbound, neighbours)
        return list(results)

    def slide(self, token):
        """
        Input: token
        Output: ["SLIDE", before, after]
        """
        (s, r, q) = token
        before = (r, q)
        nbr = self.neighbours(before)
        return [("SLIDE", before, after) for after in nbr]

    def swing(self, token, player):
        """
        Input: token, player
        Output: ["SWING", before, after]
        """
        (s, r, q) = token
        before = (r, q)
        nbr = self.neighbours(before)

        pivot = []
        for n in nbr:
            (x, y) = n
            for sym in ("r", "p", "s"):
                if player == 'upper':
                    if (sym, x, y) in self.upper:
                        pivot.append(n)
                if player == 'lower':
                    if (sym, x, y) in self.lower:
                        pivot.append(n)
        pivot_nbr = []
        for p in pivot:
            (x, y) = p
            for n in self.neighbours(p):
                if n != (r, q) and n not in nbr:
                    pivot_nbr.append(("SWING", before, n))
        pivot_nbr = list(dict.fromkeys(pivot_nbr))
        return pivot_nbr

    def throw(self, player):
        throwable = []
        for symbol in ("r", "p", "s"):
            if player == 'upper':
                for coord in grid:
                    if coord[0] >= (self.upper_throws - 5) and \
                        self.upper_throws > 0:
                        throwable.append(("THROW", symbol, coord))
            if player == 'lower':
                for coord in grid:
                    if coord[0] <= -(self.lower_throws - 5) and \
                        self.lower_throws > 0:
                        throwable.append(("THROW", symbol, coord))
        return throwable

    def _actions(self, player):
        actions = list()

        throwable = self.throw(player)
        actions.extend(throwable)
        if player == 'upper':
            for token in self.upper:
                actions.extend(self.slide(token))
                actions.extend(self.swing(token, player))
        if player == 'lower':
            for token in self.lower:
                actions.extend(self.slide(token))
                actions.extend(self.swing(token, player))
        return actions
        
    def filtered_actions(self, player):
        actions = self._actions(player)
        if player == 'upper':
            for action in actions:
                if action[0] == 'THROW':
                    token = self.find_token(action[-1], player)
        pass            

    def add(self):
        if self not in GAME_STATES:
            GAME_STATES[self] = 1
        else:
            GAME_STATES[self] += 1

    def _invincible(self):
        upper_symbols = {'r': 0, 'p': 0, 's': 0}
        lower_symbols = {'r': 0, 'p': 0, 's': 0}
        for token in self.upper:
            upper_symbols[token[0]] += 1
        for token in self.lower:
            lower_symbols[token[0]] += 1

        if self.lower_throws == 0:
            for token in self.upper:
                (s, r, q) = token
                if upper_symbols[s] > 0 and \
                lower_symbols[WHAT_BEATS[s]] == 0:
                    self.upper_inv = True
        if self.upper_throws == 0:
            for token in self.lower:
                (s, r, q) = token
                if lower_symbols[s] > 0 and \
                upper_symbols[WHAT_BEATS[s]] == 0:
                    self.lower_inv = True

    def end_game(self):
        # Condition 1
        # If lower has nothing
        if len(self.lower) == 0 and len(self.upper) > 0:
            if len(self.upper) > 0 or self.upper_throws > 0:
                self.game_state = 'upper'
                self.condition = 'C1'
                return True
            else:
                self.game_state = 'draw'
                self.condition = 'C1'                
                return True
        # If upper has nothing
        if len(self.upper) == 0 and len(self.lower) > 0:
            if len(self.lower) > 0 or self.lower_throws > 0:
                self.game_state = 'lower'
                self.condition = 'C1'
                return True
            else:
                self.game_state = 'draw'
                self.condition = 'C1'
                return True
        # Condition 2 (Both have an invincible token)
        if self.upper_inv == True and self.lower_inv == True:
            self.game_state = 'draw'
            self.condition = 'C2'
            return True
        # Condition 3
        # Upper is invincible and lower only has one token
        if self.upper_inv == True and len(self.lower) == 1:
            self.game_state = 'upper'
            self.condition = 'C3'
            return True
        # Lower is invincible and upper only has one token
        if self.lower_inv == True and len(self.upper) == 1:
            self.game_state = 'lower'
            self.condition = 'C3'
            return True
        # Condition 4 (Same game configuration for the 3rd time)
        if MAX_SAME_CONFIG in GAME_STATES.values():
            self.game_state = 'draw'
            self.condition = 'C4'
            return True
        # Condition 5 (Turn timer)
        if self.turn >= MAX_TURNS:
            self.game_state = 'draw'
            self.condition = 'C5'
            return True

        return False

    def get_other_player(self):
        if self.player_1 == 'upper':
            return 'lower'
        if self.player_1 == 'lower':
            return 'upper'
    
    def find_token(self, coordinate, player):
        (x, y) = coordinate
        if player == 'upper':
            for (s, r, q) in self.upper:
                if r == x and q == y:
                    return (s, r, q)
        elif player == 'lower':
            for (s, r, q) in self.lower:
                if r == x and q == y:
                    return (s, r, q)

    def read_move(self, move, player):
        if player == 'upper':
            pieces = deepcopy(self.upper)
        elif player == 'lower':
            pieces = deepcopy(self.lower)

        if move[0] == 'THROW':
            if player == 'upper':
                self.upper_throws -= 1
            elif player == 'lower':
                self.lower_throws -= 1
            (atype, s, (r, q)) = move
            pieces.append((s, r, q))
        else:
            (atype, before, after) = move
            s, r, q = self.find_token(before, player)
            (x, y) = after
            pieces.remove((s, r, q))
            pieces.append((s, x, y))
        return pieces

    def check_piece(self, p1_piece, p2_piece):
        p1_c = list()
        p2_c = list()
        for t1 in p1_piece:
            for t2 in p2_piece:
                if t1[1] == t2[1] and t1[2] == t2[2]:
                    if WHAT_BEATS[t1[0]] == t2[0]:
                        p1_c.append((t1, t2))
                    if WHAT_BEATS[t2[0]] == t1[0]:
                        p2_c.append((t2, t1))
        if p1_piece == p2_piece:
            if p1_c:
                for i in set(p1_c):
                    p1_piece.remove(i[0])
            return p1_piece, p1_piece
        else:
            if p1_c:
                for i in set(p1_c):
                    p1_piece.remove(i[0])
            if p2_c:
                for i in set(p2_c):
                    p2_piece.remove(i[0])
            return p1_piece, p2_piece

    def apply_action(self, p1_move, p2_move):
        p1 = self.read_move(p1_move, self.player_1)
        p2 = self.read_move(p2_move, self.player_2)
        for i in range(9):
            p1, p1 = self.check_piece(p1, p1)
            p2, p2 = self.check_piece(p2, p2)
            p1, p2 = self.check_piece(p1, p2)
        return p1, p2

    def update(self, player_1_pieces, player_2_pieces):
        if self.player_1 == 'upper':
            self.upper = player_1_pieces
            self.lower = player_2_pieces
        elif self.player_1 == 'lower':
            self.lower = player_1_pieces
            self.upper = player_2_pieces
        
        self.turn += 1
        self._invincible()
        self.done = self.end_game()
        

"""     
class GameState(RoPaSci360):
    def __init__(self):
        super().__init__()

        self.turn_number = 0
        self.game_state = 'running'

        self.upper_inv = False
        self.lower_inv = False

    def add(self):
        if self not in GAME_STATES:
            GAME_STATES[self] = 1
        else:
            GAME_STATES[self] += 1

    def _invincible(self):
        upper_symbols = {'r': 0, 'p': 0, 's': 0}
        lower_symbols = {'r': 0, 'p': 0, 's': 0}
        for token in self.upper:
            upper_symbols[token[0]] += 1
        for token in self.lower:
            lower_symbols[token[0]] += 1

        if self.lower_throws == 0:
            for token in self.upper:
                (s, r, q) = token
                if upper_symbols[s] > 0 and \
                lower_symbols[WHAT_BEATS[s]] == 0:
                    self.upper_inv = True
        if self.upper_throws == 0:
            for token in self.lower:
                (s, r, q) = token
                if lower_symbols[s] > 0 and \
                upper_symbols[WHAT_BEATS[s]] == 0:
                    self.lower_inv = True

    def end_game(self):
        # Condition 1
        # If lower has nothing
        if len(self.lower) == 0 and len(self.upper) > 0:
            if len(self.upper) > 0 or self.upper_throws > 0:
                self.game_state = 'upper'
                return True
            else:
                self.game_state = 'draw'
                return True
        # If upper has nothing
        if len(self.upper) == 0 and len(self.lower) > 0:
            if len(self.lower) > 0 or self.lower_throws > 0:
                self.game_state = 'lower'
                return True
            else:
                self.game_state = 'draw'
                return True
        # Condition 2 (Both have an invincible token)
        if self.upper_inv == True and self.lower_inv == True:
            self.game_state = 'draw'
            return True
        # Condition 3
        # Upper is invincible and lower only has one token
        if self.upper_inv == True and len(self.lower) == 1:
            self.game_state = 'upper'
            return True
        # Lower is invincible and upper only has one token
        if self.lower_inv == True and len(self.upper) == 1:
            self.game_state = 'lower'
            return True
        # Condition 4 (Same game configuration for the 3rd time)
        if MAX_SAME_CONFIG in GAME_STATES.values():
            self.game_state = 'draw'
            print('c4')
            return True
        # Condition 5 (Turn timer)
        if self.turn_number >= MAX_TURNS:
            self.game_state = 'draw'
            return True

        return False
"""