import numpy as np

LEFT        = (0, -1)
RIGHT       = (0, +1)
UP_LEFT     = (-1, 0)
UP_RIGHT    = (-1, +1)
DOWN_LEFT   = (+1, -1)
DOWN_RIGHT  = (+1, 0)

NEIGHBOURS = [RIGHT, DOWN_RIGHT, DOWN_LEFT, LEFT, UP_LEFT, UP_RIGHT]

TOKEN_EMPTY = '_'
TOKEN_VOID = np.inf

BOARD_SIZE = 9

N_THROWS = 9

BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}

MAX_TURNS = 360
MAX_SAME_CONFIG = 3

# Upper
ROCK = 'R'
PAPER = 'P'
SCISSOR = 'S'
UPPER = (ROCK, PAPER, SCISSOR)
# Lower
rock = 'r'
paper = 'p'
scissor = 's'
LOWER = (rock, paper, scissor)

class RoPaSci360:
    def __init__(self):
        self.board = None
        self.upper_pcs = None
        self.lower_pcs = None

        self.upper_inv = None
        self.lower_inv = None

        # Current
        self.upper_throws = 9
        self.lower_throws = 9
        self.upper_turns = None
        self.lower_turns = None
        self.game_state = None

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
                        TOKEN_EMPTY, dtype = np.object_)
        for i in range(BOARD_SIZE // 2):
            board[i, i + 5:BOARD_SIZE] = TOKEN_VOID
            board[i + 5:BOARD_SIZE, i] = TOKEN_VOID
        return board

    @staticmethod
    def convert_to_axial(position):
        (r, q) = position
        return (BOARD_SIZE // 2 - r, q - BOARD_SIZE // 2)

    @staticmethod
    def convert_to_normal(position):
        (r, q) = position
        return (BOARD_SIZE // 2 - r, q + BOARD_SIZE // 2)

    @staticmethod
    def get_tokens(board, symbol):
        res = np.where(board == symbol)
        return [(symbol, p[0], p[1]) for p in list(zip(res[0], res[1]))]

    def get_upper(self):
        upper = list()
        for symbol in UPPER:
            for i in self.get_tokens(self.board, symbol):
                (s, x, y) = i
                coord = self.convert_to_axial((x, y))
                (r, q) = coord
                upper.append((symbol, r , q))
        return upper

    def get_lower(self):
        lower = list()
        for symbol in LOWER:
            for i in self.get_tokens(self.board, symbol):
                (s, x, y) = i
                coord = self.convert_to_axial((x, y))
                (r, q) = coord
                lower.append((symbol, r , q))
        return lower

    @staticmethod
    def get_neighbours(token):
        (s, r, q) = token
        return [(s, r + x, q + y) for (x, y) in NEIGHBOURS]

    #==================== Check Move =========================#
    def inbound(self, token):
        (s, r, q) = token
        if abs(r) > (BOARD_SIZE // 2) or abs(q) > (BOARD_SIZE // 2):
            return False
        res = np.where(self.board == np.inf)
        out_of_bound = [i for i in list(zip(res[0], res[1]))]
        if self.convert_to_normal((r,q)) in out_of_bound:
            return False
        return True

    def check_slide(self, before, after):
        slide = list(filter(self.inbound, self.get_neighbours(before)))
        if after in slide:
            return ("SLIDE", before, after)
        return ("INVALID", before, after)

    def check_swing(self, before, after, player):
        nbr = self.get_neighbours(before)

        pivot = list()
        for n in nbr:
            (s_b, x, y) = n
            if player == 'Upper':
                tokens = self.get_upper()
                for s in UPPER:
                    if (s, x, y) in tokens:
                        pivot.append((s, x, y))
            if player == 'Lower':
                tokens = self.get_lower()
                for s in LOWER:
                    if (s, x, y) in tokens:
                        pivot.append((s, x, y))
        swing = list()
        for token in pivot:
            for n in self.get_neighbours(token):
                if n != before and n not in nbr:
                    swing.append(n)
        swing = list(dict.fromkeys(swing))
        if after in swing:
            return ("SWING", before, after)
        return ("INVALID", before, after)

    def check_throw(self, token, player):
        (s, r, q) = token
        if self.inbound(token):
            if player == 'Upper':
                if r >= self.upper_throws - 5:
                    return ("THROW", s, (r, q))
            if player == 'Lower':
                if r <= 5 - self.lower_throws:
                    return ("THROW", s, (r, q))
        return ("INVALID", None, token)
