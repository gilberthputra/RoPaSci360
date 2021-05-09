from ADDITIONAL_PYLON.state import *
from random import choice
from ADDITIONAL_PYLON.heuristic import *
from ADDITIONAL_PYLON.SMAB import *
from math import inf
from copy import deepcopy

import time

def main():
    game = RoPaSci360(player = 'upper')


    book = [('THROW', 'r', (4, -4)), ('THROW', 'p', (4, -3)), ('THROW', 's', (3, -3)),
            ('THROW', 'r', (4, -1)), ('THROW', 'p', (4, 0)), ('THROW', 's', (3, 0))]
    for action in book:
        p2_act = game._actions(game.player_2)
        c2 = choice(p2_act)
        p1, p2 = game.apply_action(action, c2)
        game.update(p1, p2)
    #start = time.perf_counter()
    
    """
    for i in range(20):
        if not game.done:
            p2_act = game._actions(game.player_2)
            c2 = choice(p2_act)
            payoff, action = SMAB(tmp_game, mid_game, alpha = -inf, beta = inf, depth = 1)
            p1, p2 = game.apply_action(action, c2)
            game.update(p1, p2)
    """
            
    
    
    print(cost_to_enemy(game, game.player_1))
    print(cost_from_enemy(game, game.player_1))
    print(save_throws(game, game.player_1))
    print(targeted_throw(game, game.player_1))
    #SMAB_strat(game, mid_game, strat, alpha = -inf, beta = inf,depth = 2)
    start = time.perf_counter()
    payoff, action = SMAB(game, mid_game, alpha = -inf, beta = inf, depth = 2)
    print(payoff)
    print(action)
    end = time.perf_counter()
    print('Time taken:', end - start)
    
main()