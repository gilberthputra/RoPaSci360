from state import *
from random import choice
from heuristic import *
from SMAB import *

def main():
    game = RoPaSci360(player = 'upper')
    """
    for i in range(100):
        p1_act = game._actions(game.player_1)
        p2_act = game._actions(game.player_2)
        c1 = choice(p1_act)
        c2 = choice(p2_act)
        game.update(c1, c2)
        print(game.upper)
        print(game.lower)
        print('upper', advantage(game, game.player_1))
        print('lower', advantage(game, game.player_2))
    
    for i in range(400):
        p1_act = game._actions(game.player_1)
        p2_act = game._actions(game.player_2)
        c1 = choice(p1_act)
        c2 = choice(p2_act)
        p1, p2 = game.apply_action(c1, c2) 
        game.update(p1, p2)
    
    for i in range(10):
        game = RoPaSci360(player = 'upper')
        for j in range(400):
            if not game.done:
                print("TURN NUMBER", game.turn)
                print("UPPER BEFORE", game.upper)
                print("+++++++++++++++++++++++++++++++")
                print("LOWER BEFORE", game.lower)
                
                p1_act = game._actions(game.player_1)
                p2_act = game._actions(game.player_2)
                c1 = choice(p1_act)
                c2 = choice(p2_act)
                print("=================================")
                print("LOWER ACTION", c1)
                print("UPPER ACTION", c2)
                p1, p2 = game.apply_action(c1, c2)
                game.update(p1, p2)
                print("=================================")
                print("UPPER AFTER", game.upper)
                print("NO OF TOKENS UPPER", len(game.upper))
                print("UPPER THROWS", game.upper_throws)
                print("+++++++++++++++++++++++++++++++")
                print("LOWER AFTER", game.lower)
                print("NO OF TOKENS LOWER", len(game.lower))
                print("Lower Throws", game.lower_throws)
                print("\n")

    """    
    """print(game.game_state) print(game.condition)"""


    for i in range(20):
        p1_act = game._actions(game.player_1)
        p2_act = game._actions(game.player_2)
        c1 = choice(p1_act)
        c2 = choice(p2_act)
        p1, p2 = game.apply_action(c1, c2)
        game.update(p1, p2)
    SMAB(game, mid_game, alpha = -55, beta = 55,depth = 1)
    
main()