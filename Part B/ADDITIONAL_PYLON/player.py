from ADDITIONAL_PYLON.state import *
from random import choice
from ADDITIONAL_PYLON.heuristic import *
from ADDITIONAL_PYLON.adversarial import *
from math import inf
from copy import deepcopy

BOOK_1 = [('THROW', 'r', (4, -4)), ('THROW', 'p', (4, -3)),
        ('THROW', 's', (3, -3)), ('THROW', 'r', (4, -1)),
        ('THROW', 'p', (4, 0)), ('THROW', 's', (3, 0))]

BOOK_2 = [('THROW', 'r', (-4, 4)), ('THROW', 'p', (-4, 3)),
        ('THROW', 's', (-3, 3)), ('THROW', 'r', (-4, 1)),
        ('THROW', 'p', (-4, 0)), ('THROW', 's', (-3, 0))]

AG_BOOK_1 = [('THROW', 'r', (4, -2)), ('THROW', 'p', (3, -2)),
            ('THROW', 's', (2, -1)), ('THROW', 'p', (1, 0)),
            ('THROW', 'r', (0, 0)), ('THROW', 's', (-1, 0))]


class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        self.game = RoPaSci360(player = player)
        self.book = AG_BOOK_1 if player == 'upper' else BOOK_2

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        if self.book:
            return self.book.pop(0)
        else:
            payoff, action = SMAB_cell_ordering(self.game, greedy, -10000, 10000, 1)
            return action

    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        print('player 1:', player_action)
        print('player 2:', opponent_action)
        p1, p2 = self.game.apply_action(player_action, opponent_action)
        self.game.update(p1, p2)
