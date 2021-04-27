import sys
import json
import math
import typing
import itertools
import collections

#HEX_RANGE = range(-4, +4+1)
# Create the board and all legal coordinates for RoPaSci360
#ALL_HEXES = frozenset(
#        Hex(r, q) for r in HEX_RANGE for q in HEX_RANGE if -r-q in HEX_RANGE
#    )
#HEX_STEPS = [Hex(r, q) for r, q in [(1,-1),(1,0),(0,1),(-1,1),(-1,0),(0,-1)]] # Neighbours of the current pieces.

BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

MAX_TURNS = 360
MAX_SAME_CONFIG = 3
MAX_BOUNDS = 4

grid = []
for r in range(-MAX_BOUNDS, MAX_BOUNDS+1):
    for q in range(-MAX_BOUNDS, MAX_BOUNDS+1):
        grid.append((r, q))

class RoPaSci360:
    def __init__(self):
        self.upper_tokens = {'r':[], 's':[], 'p':[]}
        self.lower_tokens = {'r':[], 's':[], 'p':[]}

        self.turn_number = 0
        self.game_state = 'running'

        self.upper_throws = 9
        self.lower_throws = 9

        self.upper_inv = False
        self.lower_inv = False

        self.game_states = []

        #Potential moves are:
        # throw, throwing a token onto the board
        # slide, move a token to an adjacent hex
        # swing, move a token over an adjacent friendly token
        self.moves = (('throw', token_type, (r, q)), ('slide', (r0, q0), (r1, q1)), ('swing', (r0, q0), (r1, q1)))

    #Checks if the game has ended or not
    def end_game(self):
        #Turn timer
        if self.turn_number >= MAX_TURNS:
            self.game_state = 'draw'
            return True
        #Both players are invincible
        if self.upper_inv == True and self.lower_inv == True:
            self.game_state = 'draw'
            return True
        #Upper is invincible and lower only has one token
        if self.upper_inv == True and self.tokens_remaining(self, self.lower_tokens) == 1:
            self.game_state = 'upper'
            return True
        #Lower is invincible and upper only has one token
        if self.lower_inv == True and self.tokens_remaining(self, self.upper_tokens) == 1:
            self.game_state = 'lower'
            return True
        #Lower has nothing
        if self.lower_throws == 0 and self.tokens_remaining(self, self.lower_tokens) == 0:
            if self.upper_throws > 0 or self.tokens_remaining(self, self.upper_tokens) > 0:
                self.game_state = 'upper'
                return True
            else:
                self.game_state = 'draw'
                return True
        #Upper has nothing
        if self.upper_throws == 0 and self.tokens_remaining(self, self.upper_tokens) == 0:
            if self.lower_throws > 0 or self.tokens_remaining(self, self.lower_tokens) > 0:
                self.game_state = 'lower'
                return True
            else:
                self.game_state = 'draw'
                return True
        #Same game configuration occurs for the third time
        for count in collections.Counter(game_states).values():
            if count == MAX_SAME_CONFIG:
                self.game_state = 'draw'
                return True

        #Keep going
        return False

    #Finds if a player has any invincible tokens and declares the player as invincible, invincibility cannot be stripped
    def set_invincible(self):
        if self.lower_throws == 0:
            for token in self.upper_tokens:
                if len(token) > 0 and len(self.lower_tokens[BEATS_WHAT[token]]):
                    self.upper_inv = True
        if self.upper_throws == 0:
            for token in self.lower_tokens:
                if len(token) > 0 and len(self.upper_tokens[BEATS_WHAT[token]]):
                    self.lower_inv = True

    #Finds how many tokens a player has left
    def tokens_remaining(self, tokens):
        sum = 0
        for token in tokens:
            sum += len(token)
        return sum

    #Adds a game state to the list of game states
    def add_game_state(self):
        game_state = GameState(self)
        self.game_states.append(game_state)

    def inbound(self, location):
        (r, q) = location
        if abs(r) > MAX_BOUNDS or abs(q) > MAX_BOUNDS:
            return False
        
        list = []
        i = MAX_BOUNDS
        x = 0
        while i > 0:
            x += 1
            for j in range(x, MAX_BOUNDS + 1):
                list.append((i,j))
                list.append((-i,-j))
            i -= 1

        return location not in list

    def neighbours(self, location):
        (r, q) = location
        ## Neighbours in order of Top-Left, Top-Right, Mid-Left, Mid-Right,
        ## Bottom-Left, Bottom-Right
        neighbours = [(r + 1, q - 1), (r + 1, q),
                      (r, q - 1), (r, q + 1),
                      (r - 1, q), (r - 1, q + 1)]

        results = filter(self.inbound, neighbours)
        #results = list(filter(self.passable, results))
        return results

    def slide(self, token):
        symbol = token[0]
        lctn = token[1]
        nbr = self.neighbours(lctn)
        return [(symbol, i) for i in nbr]

    def swing(self, token, player):
        symbol = token[0]
        lctn = tuple(token[1])

        nbr = self.neighbours(lctn)

        pivot = []
        for n in nbr:
            if player == 'upper':
                tmp = self.upper_tokens['r'] + self.upper_tokens['s'] + self.upper_tokens['p']
            elif player == 'lower':
                tmp = self.lower_tokens['r'] + self.lower_tokens['s'] + self.lower_tokens['p']
            if n in tmp:
                pivot.append(n)

        pivot_nbr = [(symbol, n) for p in pivot for n in self.neighbours(p) \
                    if n != lctn and n not in nbr]
        pivot_nbr = list(dict.fromkeys(pivot_nbr))

        return pivot_nbr

    def throw(self, token, player):
        hexgrid = filter(self.inbound, grid)
        throwable = []
        if player == 'upper':
            for coord in hexgrid:
                if coord[0] >= (self.upper_throws - 5):
                    throwable.append(coord)
        if player == 'lower':
            for coord in hexgrid:
                if coord[0] <= -(self.lower_throws - 5):
                    throwable.append(coord)

        return throwable





    class GameState:
        def __init__(self, rps360):
            self.upper_tokens = rps360.upper_tokens
            self.lower_tokens = rps360.lower_tokens

            self.upper_throws = rps360.upper_throws
            self.lower_throws = rps360.lower_throws