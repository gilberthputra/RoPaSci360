import collections
import heapq

T = TypeVar('T')

##********************************* CLASSES *********************************##
##** ROPASCI BOARD **********************************************************##
## Implemented and inspired from
## (www.redblobgames.com/pathfinding/a-star/implementation.html)

class RoPaSci360:
    def __init__(self, row, column, blocks):
        self.row = row
        self.column = column
        self.blocks = blocks

    def inbound(self, position):
        (r, q) = position
        if abs(r) > (self.column // 2) or abs(q) > (self.column // 2):
            return False

        list = [(4, 1), (4, 2), (4, 3), (4, 4), (3, 2),
                (3, 3), (3, 4), (2, 3), (2, 4), (1, 4),
                (-1, -4), (-2, -4), (-2, -3), (-3, -4), (-3, -3),
                (-3, -2), (-4, -4), (-4, -3), (-4, -2), (-4, -1)]

        return position not in list

    def passable(self, position):
        (r, q) = position
        return ('', r, q) not in self.blocks

    def neighbours(self, position):
        (r, q) = position
        ## Neighbours in order of Top-Left, Top-Right, Mid-Left, Mid-Right,
        ## Bottom-Left, Bottom-Right
        neighbours = [(r + 1, q - 1), (r + 1, q),
                      (r, q - 1), (r, q + 1),
                      (r - 1, q), (r - 1, q + 1)]

        results = filter(self.inbound, neighbours)
        results = list(filter(self.passable, results))
        return results

##** BOARD STATE ************************************************************##

class state:

    def __init__(self, upper, lower, board):
        self.board = board
        self.upper = upper
        self.lower = lower

    def rules(self, token):
        (symbol, r, q) = token
        if symbol == 'p':
            if ('s', r, q) in self.upper or ('s', r, q) in self.lower:
                return False
        if symbol == 's':
            if ('r', r, q) in self.upper or ('r', r, q) in self.lower:
                return False
        if symbol == 'r':
            if ('p', r, q) in self.upper or ('p', r, q) in self.lower:
                return False
        return True

    def actions_successors(self):
        actions_successors_list = []
        for action in self._actions():
            actions_successors_list.append((action, self._apply(action)))
        return actions_successors_list

    def slide(self, token):
        (s, r, q) = token
        tmp = [(s, n[0], n[1]) for n in self.board.neighbours((r, q))]
        return list(filter(self.rules, tmp))

    def swing(self, token, player):
        (s, r, q) = token
        nbr = self.board.neighbours((r,q))

        pivot = []
        for n in nbr:
            (x, y) = n
            for sym in ['r', 'p', 's']:
                if player == 'upper':
                    if (sym, x, y) in self.upper:
                        pivot.append(n)
                if player == 'lower':
                    if (sym, x, y) in self.lower:
                        pivot.append(n)
        pivot_nbr = []
        for p in pivot:
            (x, y) = p
            for n in self.board.neighbours(p):
                (n1, n2) = n
                if n != (r, q) and n not in nbr:
                    pivot_nbr.append((s, n1, n2))
        pivot_nbr = list(dict.fromkeys(pivot_nbr))

        return pivot_nbr

    def possible_actions(self, token, player = None):

        if player is None:
            player = 'upper'

        results = []

        results.extend([(i, 1) for i in self.slide(token)])
        results.extend([(i, 2) for i in self.swing(token, player)])

        return results

    def _actions(self):

        available_actions = {}
        for upper in self.upper:
            available_actions[upper] = []
        for upper in self.upper:
            for action in self.possible_actions(upper):
                available_actions[upper].append(action)
        print(available_actions)

    def _apply(self, action):
        (curr, next, atype) = action
        return state(self.upper - {curr} | {next}, self.lower, self.board)

    def update(self, prev_move, curr_move, player):
        if player == 'upper':
            self.upper[prev_move[0]].remove(prev_move[1])
            self.upper[curr_move[0]].append(curr_move[1])
            return state(self.upper, self.lower, self.board)
        elif player == 'lower':
            self.lower[prev_move[0]].remove(prev_move[1])
            self.lower[curr_move[0]].append(curr_move[1])
            return state(self.upper, self.lower, self.board)

    def __eq__(self, other):
        return self.upper == other.upper

    def __hash__(self):
        return hash(self.upper)

##** PRIORITY QUEUE *********************************************************##
## Implemented from
## (www.redblobgames.com/pathfinding/a-star/implementation.html)

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return not self.elements

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]
