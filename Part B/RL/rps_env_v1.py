from gym import Env
from gym.spaces import Discrete, Box, Dict

from state import *
from copy import deepcopy
from random import choice

import numpy as np

INVALID_ACTION_REWARD = -10
VALID_ACTION_REWARD   = 10
WIN_REWARD            = 100
DRAW_REWARD           = 0
LOSS_REWARD           = -100
CAPTURED              = -10
EAT_TOKEN             = 10

MAX_TURNS             = 360
MAX_SAME_CONFIG       = 3
MAX_THROWS            = 9
BOARD_SIZE            = 9

EMPTY = (0, 0, 0)

TOKEN_EMPTY = 0
TOKEN_VOID = -2

ROCK = 1
PAPER = 2
SCISSOR = 3
SYMBOLS = (ROCK, PAPER, SCISSOR)

PRINT_SYM = {1: 'R', 2: 'P', 3: 'S'}

BEATS_WHAT = {ROCK: SCISSOR, PAPER: ROCK, SCISSOR: PAPER}
WHAT_BEATS = {SCISSOR: ROCK, ROCK: PAPER, PAPER: SCISSOR}

# Axial grid system
AXIAL_GRID = [(4, -4), (4, -3), (4, -2), (4, -1), (4, 0), 
        (3, -4), (3, -3), (3, -2), (3, -1), (3, 0), (3, 1), 
        (2, -4), (2, -3), (2, -2), (2, -1), (2, 0), (2, 1), (2, 2), 
        (1, -4), (1, -3), (1, -2), (1, -1), (1, 0), (1, 1), (1, 2), (1, 3), 
        (0, -4), (0, -3), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2), (0, 3), (0, 4), 
        (-1, -3), (-1, -2), (-1, -1), (-1, 0), (-1, 1), (-1, 2), (-1, 3), (-1, 4), 
        (-2, -2), (-2, -1), (-2, 0), (-2, 1), (-2, 2), (-2, 3), (-2, 4), 
        (-3, -1), (-3, 0), (-3, 1), (-3, 2), (-3, 3), (-3, 4), 
        (-4, 0), (-4, 1), (-4, 2), (-4, 3), (-4, 4)] 
AXIAL_POS = {}
for pos in range(len(AXIAL_GRID)):
    AXIAL_POS[pos] = AXIAL_GRID[pos]

LEFT        = (0, -1)
RIGHT       = (0, +1)
UP_LEFT     = (-1, 0)
UP_RIGHT    = (-1, +1)
DOWN_LEFT   = (+1, -1)
DOWN_RIGHT  = (+1, 0)

NEIGHBOURS = [RIGHT, DOWN_RIGHT, DOWN_LEFT, LEFT, UP_LEFT, UP_RIGHT]


class RoPaSci360(Env):
    def __init__(self, player = 'upper', opponent = 'random', log = True):
        assert player=='upper' or player =='lower', "Put player as either 'upper' or 'lower'"
        self.max_turns = MAX_TURNS
        self.log = log
        #
        # Observation + Action spaces
        # ---------------------------
        #  Observations: np.array with shape (9, 3) containing (symbol, r, q) in each array 
        #                for both players.
        #  Actions: Dictionary consists of symbol with 3 options (ROCK, PAPER, SCISSOR) and 
        #           position from 0 to 61 which position 0 mean a throw action.
        #
        # Note: not every action is legal
        #

        self.action_space = Dict({"symbol": Discrete(3), "position": Box(0, 61, shape = (2,), dtype=np.int8)})
        self.observation_space = Box(low = np.int8(0), high = np.int8(-1), shape = (9, 9), dtype = np.int8)
        #self.observation_space = Dict({'upper': Box(low = np.int8(0), high = np.int8(-1), shape = (9, 3), dtype = np.int8),
        #                               'lower': Box(low = np.int8(0), high = np.int8(-1), shape = (9, 3), dtype = np.int8)})

        self.player_1 = player
        self.player_2 = self.get_other_player()
        self.opponent = opponent

        self.reset()

    def reset(self):
        self.board = self.new_board()
        self.pieces = {'upper': np.full((9, 3), 0, dtype = np.int8),
                       'lower': np.full((9, 3), 0, dtype = np.int8)}
        self.upper_inv = False
        self.lower_inv = False

        self.throw = {'upper': MAX_THROWS, 'lower': MAX_THROWS}
        self.turn = {'upper': 0, 'lower': 0}
        self.eat = {'upper': 0, 'lower': 0}

        self.info = {'turn': self.turn[self.player_1], 'moves': list(), 
                     'player': self.player_1, 'state': 'running'}

        #self.game_states = {}

        self.done = False
        
    @staticmethod
    def new_board():
        """
        return a new board with no tokens

        Returns:
            numpy.ndarray: the new board

        Examples:
            >>> print(RoPaSci360.new_board())
               [['_' '_' '_' '_' '_' inf inf inf inf]
                ['_' '_' '_' '_' '_' '_' inf inf inf]
                ['_' '_' '_' '_' '_' '_' '_' inf inf]
                ['_' '_' '_' '_' '_' '_' '_' '_' inf]
                ['_' '_' '_' '_' '_' '_' '_' '_' '_']
                [inf '_' '_' '_' '_' '_' '_' '_' '_']
                [inf inf '_' '_' '_' '_' '_' '_' '_']
                [inf inf inf '_' '_' '_' '_' '_' '_']
                [inf inf inf inf '_' '_' '_' '_' '_']]
        """
        n = BOARD_SIZE
        board = np.full((BOARD_SIZE, BOARD_SIZE), \
                        TOKEN_EMPTY, dtype = np.int8)
        for i in range(BOARD_SIZE // 2):
            board[i, i + 5:BOARD_SIZE] = TOKEN_VOID
            board[i + 5:BOARD_SIZE, i] = TOKEN_VOID
        return board
    
    def step(self, action): 
        assert self.action_space.contains(action), "ACTION ERROR {}".format(action)

        if self.done:
            return self.board, 0, True, self.info

        player_1_valid = False
        reward = 0
        symbol = action['symbol'] + 1
        pos1, pos2 = action['position']
        move_check = self.validate_move(symbol, pos1, pos2, self.player_1)
        pieces = deepcopy(self.pieces)

        # Update player_1 move
        if move_check:
            (atype, before, after) = move_check
            pieces = self.update(pieces, self.player_1, before, after)

            if atype == 'THROW':
                self.throw[self.player_1] -= 1

            self.turn[self.player_1] += 1
            player_1_valid = True
            reward += VALID_ACTION_REWARD
        else:
            return self.board, INVALID_ACTION_REWARD, self.done, self.info

        # Opponent play
        if player_1_valid:
            opp_move = self.random_agent()
            (atype_o, before_opp, after_opp) = opp_move
            if atype == 'THROW':
                self.throw[self.player_2] -= 1
            pieces = self.update(pieces, self.player_2, before_opp, after_opp)
            pieces, eaten = self.check_board(pieces)

            self.info['turn'] = self.turn[self.player_1]
            self.info['moves'].append(move_check)
            self.turn[self.player_2] += 1

            if eaten:
                reward += self.captured(eaten)
            if self.game_over(pieces):
                reward += self.reward()
                self.done = True

            self.pieces = pieces
            self.board = self.insert_to_board(self.pieces)
            #self.add_state(self.pieces)
        return self.board, reward, self.done, self.info

    def render(self): pass

    def get_other_player(self):
        if self.player_1 == 'upper':
            return 'lower'
        elif self.player_1 == 'lower':
            return 'upper'
     
    def get_upper(self, pieces = False):
        if pieces:
            upper = [u for u in pieces['upper'].tolist() if u != [0, 0, 0]]
            return np.array(upper)
        upper = [u for u in self.pieces['upper'].tolist() if u != [0, 0, 0]]
        return np.array(upper)

    def get_lower(self, pieces = False):
        if pieces:
            lower = [l for l in pieces['lower'].tolist() if l != [0, 0, 0]]
            return np.array(lower)
        lower = [l for l in self.pieces['lower'].tolist() if l != [0, 0, 0]]
        return np.array(lower)

    def get_tokens(self, player, pieces = False):
        if player == 'upper':
            return self.get_upper(pieces)
        elif player == 'lower':
            return self.get_lower(pieces)

    def update(self, pieces, player, before, after):
        before = list(before)
        after = list(after)
        arr = pieces[player].tolist()
        if before in arr:
            arr.remove(before)
            arr.append(after)
        pieces[player] = np.array(arr)
        return pieces

    @staticmethod
    def get_neighbours(token):
        (s, r, q) = token
        nbr = [(r + x, q + y) for (x, y) in NEIGHBOURS]
        return [(s, x, y) for (x, y) in nbr if (x, y) in AXIAL_GRID]

    def check_slide(self, before, after = None, possible = False):
        slide = self.get_neighbours(before)
        if possible:
            return [("SLIDE", before, s) for s in slide]
        if after in slide:
            return ("SLIDE", before, after)
        return False

    def check_swing(self, player, before, after = None, possible = False):
        nbr = self.get_neighbours(before)
        tokens = tuple(map(tuple, self.get_tokens(player)))
        pivot = [(s, r, q) for (s_n, r, q) in nbr for s in SYMBOLS if (s, r, q) in tokens]
        swing = [n for p in pivot for n in self.get_neighbours(p) \
                 if n != before and n not in nbr]
        swing = list(dict.fromkeys(swing))
        swing = list(map(tuple, swing))
        if possible:
            return [("SWING", before, s) for s in swing]
        if after in swing:
            return ("SWING", before, after)
        return False
    
    def check_throw(self, player, token = False, possible = False):
        throwable = list()
        for s in SYMBOLS:
            for coord in AXIAL_GRID:
                if player == 'upper':
                    if coord[0] >= self.throw['upper'] - 5:
                        throwable.append(("THROW", EMPTY, (s , coord[0], coord[1])))
                if player == 'lower':
                    if coord[0] <= 5 - self.throw['lower']:
                        throwable.append(("THROW", EMPTY, (s , coord[0], coord[1])))
        if possible:
            return throwable
        if token:
            if ("THROW", EMPTY, token) in throwable:
                return ("THROW", EMPTY, token) 
        return False

    def validate_move(self, symbol, before, after, player):
        if after == 0:
            return False
        tokens = self.get_tokens(player)
        after = AXIAL_POS[after - 1]
        after = (symbol, after[0], after[1])

        if before == 0:
            return self.check_throw(player, token = after)

        before = AXIAL_POS[before - 1]
        before = (symbol, before[0], before[1])

        if before not in tokens:
            return False

        move_check = self.check_swing(player, before = before, after = after)
        if move_check:
            return move_check

        move_check = self.check_slide(before, after)
        if move_check:
            return move_check
        return False 

    def possible_moves(self, player):
        possible = True
        tokens = tuple(map(tuple, self.get_tokens(player)))
        actions = list()
        actions.extend(self.check_throw(player, possible = possible))
        for t in tokens:
            actions.extend(self.check_swing(player, before = t, possible = possible))
            actions.extend(self.check_slide(t, possible = possible))
        return actions

    def random_agent(self):
        possible_moves = self.possible_moves(player = self.player_2)
        return choice(possible_moves)

    def check_board(self, pieces):
        p1 = self.get_tokens(self.player_1, pieces = pieces)
        p2 = self.get_tokens(self.player_2, pieces = pieces)
        eaten = False
        for piece_1 in p1:
            (s_1, r1, q1) = piece_1
            for piece_2 in p2:
                (s_2, r2, q2) = piece_2
                if r1 == r2 and q1 == q2:
                    if WHAT_BEATS[s_1] == s_2:
                        pieces = self.update(pieces, self.player_1, piece_1, EMPTY)
                        eaten = self.player_1
                        self.eat[self.player_2] += 1
                    if WHAT_BEATS[s_2] == s_1:
                        pieces = self.update(pieces, self.player_2, piece_2, EMPTY)
                        self.eat[self.player_1] += 1
                        eaten = self.player_2
        return pieces, eaten

    def captured(self, eaten):
        if eaten == self.player_1:
            return CAPTURED
        if eaten == self.player_2:
            return EAT_TOKEN

    def _invincible(self):
        p1_symbols = {1: 0, 2: 0, 3: 0}
        p2_symbols = {1: 0, 2: 0, 3: 0}

        for token in self.get_tokens(self.player_1):
            p1_symbols[token[0]] += 1
        for token in self.get_tokens(self.player_2):
            p2_symbols[token[0]] += 1

        if self.throw[self.player_2] == 0:
            for token in self.get_tokens(self.player_1):
                (s, r, q) = token
                if p1_symbols[s] > 0 and \
                p2_symbols[WHAT_BEATS[s]] == 0:
                    self.upper_inv = True
        if self.throw[self.player_1] == 0:
            for token in self.get_tokens(self.player_2):
                (s, r, q) = token
                if p2_symbols[s] > 0 and \
                p1_symbols[WHAT_BEATS[s]] == 0:
                    self.lower_inv = True

    def game_over(self, pieces):
        # Condition 1
        # If lower has nothing
        if len(self.get_tokens('lower', pieces)) == 0 and len(self.get_tokens('upper', pieces)) > 0:
            if len(self.get_tokens('upper', pieces)) > 0 or self.throw['upper'] > 0:
                self.info['state'] = 'upper'
                return True
            else: 
                self.info['state'] = 'draw'
                return True
        # If upper has nothing
        if len(self.get_tokens('upper', pieces)) == 0 and len(self.get_tokens('lower', pieces)) > 0:
            if len(self.get_tokens('lower', pieces)) > 0 or self.throw['lower'] > 0:
                self.info['state'] = 'lower'
                return True
            else: 
                self.info['state'] = 'draw'
                return True
        # Condition 2
        if self.upper_inv == True and self.lower_inv == True:
            self.info['state'] = 'draw'
            return True
        # Condition 3
        # Upper is invincible and lower has only one token:
        if self.upper_inv == True and len(self.get_tokens('lower', pieces)) == 1:
            self.info['state'] = 'upper'
            return True
        # Lower is invincible and upper has only one token:
        if self.lower_inv == True and len(self.get_tokens('upper', pieces)) == 1:
            self.info['state'] = 'lower'
            return True
        # Condition 4
        #if MAX_SAME_CONFIG in GAME_STATES.values():
        #    self.info['state'] = 'draw'
        #    return True
        # Condition 5
        if self.turn['upper'] >= MAX_TURNS and self.turn['lower'] >= MAX_TURNS:
            self.info['state'] = 'draw'
            return True
        
    def reward(self):
        if self.info['state'] == 'draw':
            return DRAW_REWARD
        elif self.info['state'] == player_1:
            return WIN_REWARD
        elif self.info['state'] == player_2:
            return LOSS_REWARD

    def add_state(self, pieces):
        if pieces not in self.game_states:
            self.game_states[pieces] = 1
        else:
            self.game_states[pieces] += 1
    
    @staticmethod
    def convert_to_normal(position):
        (r, q) = position
        return (BOARD_SIZE // 2 - r, q + BOARD_SIZE // 2)

    def insert_to_board(self, pieces):
        board = self.new_board()
        p1 = self.get_tokens(self.player_1, pieces)
        p2 = self.get_tokens(self.player_2, pieces)

        for p1_t in p1:
            (s, r, q) = p1_t
            (x, y) = self.convert_to_normal((r, q))
            board[x][y] = s
        for p2_t in p2:
            (s, r, q) = p2_t
            (x, y) = self.convert_to_normal((r, q))
            board[x][y] = s
        
        return board