from state import *
from gametheory import *
import numpy as np
import sys

MAX_DEPTH = 2
E = sys.float_info.epsilon

def is_dominated(lower_bound, upper_bound):
    (r, q) = lower_bound.shape
    dominated = np.zeros(shape = (r, q), dtype = np.int8)
    
    lower_bound_max = np.max(lower_bound)
    upper_bound_min = np.min(upper_bound)

    # If a value is less than the maximum value in the lower bound,
    # then it is dominated.
    res_low = np.where(lower_bound < lower_bound_max)
    low_dom = [i for i in list(zip(res_low[0], res_low[1]))]

    res_high = np.where(upper_bound > upper_bound_min)
    high_dom = [i for i in list(zip(res_high[0], res_high[1]))]
    
    for l in low_dom:
        (row, col) = l
        dominated[row][col] = 1
    
    for h in high_dom:
        (row, col) = h
        dominated[row][col] = 1

    return dominated


def SMAB(state, heuristic, alpha, beta, depth = MAX_DEPTH):
    print("START")
    print('DEPTH', depth)
    if depth == 0 :
        evals = heuristic(state, state.player_1)
        print("RETURN", evals, type(evals))
        return (evals, None)
    
    max_player = state.player_1
    min_player = state.player_2

    min_actions = state._actions(min_player)
    max_actions = state._actions(max_player)
    print(max_actions)

    min_val = np.full((len(max_actions), len(min_actions)), alpha)
    max_val = np.full((len(max_actions), len(min_actions)), beta)

    dominated = is_dominated(min_val, max_val)
    
    for A in range(len(max_actions)):
        for B in range(len(min_actions)):
            if not dominated[A][B]:
                print(dominated[A][B])
                next_state = deepcopy(state)
                alpha_AB = min_val[A][B]
                beta_AB = max_val[A][B]

                p1, p2 = next_state.apply_action(max_actions[A], min_actions[B])
                next_state.update(p1, p2)
                if alpha_AB > beta_AB:
                    evals = SMAB(next_state, heuristic, alpha_AB, alpha_AB + E, depth - 1)[0]
                    if evals < alpha_AB:
                        dominated[A] = 1
                    else:
                        dominated[:, B] = 1
                else:
                    evals = SMAB(next_state, heuristic, alpha_AB, beta_AB, depth - 1)[0]
                    print("alpha_AB", alpha_AB, type(alpha_AB))
                    print("evals", evals, type(evals))
                    if evals < alpha_AB:
                        dominated[A] = 1
                    elif evals > beta_AB:
                        dominated[:, B] = 1
                    else:
                        min_val[A][B] = max_val[A][B] = evals
    print("END") 
    res_dominated = np.where(dominated == 1)
    dominated_move_row = list(set([i[0] for i in list(zip(res_dominated[0]))]))
    dominated_move_actions = [max_actions[m] for m in dominated_move_row]

    print(min_val.shape)
    for m in dominated_move_actions:
        max_actions.remove(m)
    min_val = np.delete(min_val, dominated_move_row, axis = 0)
    
    print(dominated_move_row)
    print(min_val.shape)
    print(max_actions)
    print(solve_game(min_val))
    """for move in dominated_move:
        max_actions.pop(move[0])
        np.delete(min_val, move[0], axis = 0)"""

    return solve_game(min_val)[1], solve_game(min_val)

def Backward(state, heuristic, depth = MAX_DEPTH): pass

