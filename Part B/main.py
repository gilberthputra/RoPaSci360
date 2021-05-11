from ADDITIONAL_PYLON.state import *
from random import choice
from ADDITIONAL_PYLON.heuristic import *
from ADDITIONAL_PYLON.adversarial import *
from math import inf
from copy import deepcopy

import time

def main():
    game = RoPaSci360(player = 'upper')

    
    book_1 = [('THROW', 'r', (4, -4)), ('THROW', 'p', (4, -3)), ('THROW', 's', (3, -3)),
            ('THROW', 'r', (4, -1)), ('THROW', 'p', (4, 0)), ('THROW', 's', (3, 0))]
    book_2 = [('THROW', 'r', (-4, 4)), ('THROW', 'p', (-4, 3)), 
        ('THROW', 's', (-3, 3)), ('THROW', 'r', (-4, 1)),
        ('THROW', 'p', (-4, 0)), ('THROW', 's', (-3, 0))]
    ag_book1 = [('THROW', 'r', (4, -2)), ('THROW', 'p', (3, -2)), 
            ('THROW', 's', (3, -1)), ('THROW', 'r', (2, -1)), 
            ('THROW', 'p', (1, -1)), ('THROW', 's', (1, 0))]
    while book_1:
        p1_act = book_1.pop(0)
        p2_act = game._actions(game.player_2)
        p1, p2 = game.apply_action(p1_act, choice(p2_act))
        game.update(p1, p2)
    
    for i in range(15):
        if not game.done:
            p1_act = game._actions(game.player_1)
            p2_act = game._actions(game.player_2)
            c1 = choice(p1_act)
            c2 = choice(p2_act)
            p1, p2 = game.apply_action(c1, c2)
            game.update(p1, p2)
    
    balance_token(game, game.player_1)

    #print(cost_to_enemy(game, game.player_1))
    #print(cost_from_enemy(game, game.player_1))
    #print(save_throws(game, game.player_1))
    #print(cost_to_allies(game, game.player_1))
    #print(targeted_throw(game, game.player_1))
    #if game.upper_throws == 0:
    #    SMAB_cell_ordering(game, mid_game, alpha = -10000, beta = 10000,depth = 2)
    #start = time.perf_counter()
    #print(game.upper)
    #print(game.lower)
    #payoff, action = SMAB(game, mid_game, alpha = -inf, beta = inf, depth = 1)
    #print(payoff)
    #print(action)
    #end = time.perf_counter()
    #print('Time taken:', end - start)
    #payoff, action = double_oracle(game, greedy, -1000, +1000, depth = 1)
    #print(payoff, action)
main()