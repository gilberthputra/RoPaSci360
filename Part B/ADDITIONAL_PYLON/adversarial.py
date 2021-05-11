from ADDITIONAL_PYLON.state import *
from ADDITIONAL_PYLON.gametheory import *
import scipy.optimize as opt
import numpy as np
import sys
import time

from random import choice, shuffle
from math import inf

MAX_DEPTH = 2
E = sys.float_info.epsilon
#++++++++++++++ UTILITIES ++++++++++++++#
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

def dominating_A(min_val, max_val, max_actions, dominated_row, A, B):
    x = np.ones(shape = (len(max_actions))) / len(max_actions)
    xt = x.T
    j = np.delete(min_val, B, axis = 1)
    xtj = np.dot(xt, j)
    oaj = max_val[A]
    oaj = np.delete(oaj, B, axis = 0)
    dominating_A = [i for i in range(len(xtj)) if xtj[i] > oaj[i] and i not in dominated_row]

    return dominating_A

def dominating_B(min_val, max_val, min_actions, dominated_col, A, B):
    x = np.ones(shape = (len(min_actions))) / len(min_actions)
    j = np.delete(max_val.T, A, axis = 1)
    xtj = np.dot(x, j)
    pbj = min_val[:, B]
    pbj = np.delete(pbj, A, axis = 0)
    dominating_B = [i for i in range(len(xtj)) if xtj[i] > pbj[i] and i not in dominated_col]
    return dominating_B

#+++++++++++++++ S M A B +++++++++++++++#
LOWER_BOUND = -10000
UPPER_BOUND = 10000
SKIPPING    = 1

def cal_alpha_AB(min_val, max_val, max_actions, dominated, A, B, s = SKIPPING): 
    if dominating_A(min_val, max_val, max_actions, dominated, A, B) and B >= s:
        rows, cols = min_val.shape
        x = np.ones(shape = (len(max_actions) + 1)) / (len(max_actions) + 1)
        a = np.full((1, cols), LOWER_BOUND)
        p = np.vstack((min_val, a))
        f = max_val[A]
        e = p[:,B]
        xt = x.T
        if np.all(np.dot(xt, p) > f) and np.sum(x) <= 1:
            alpha_AB = np.dot(xt, e)
            return alpha_AB
    return min_val[A][B] - 1

def cal_beta_AB(min_val, max_val, min_actions, dominated, A, B, s = SKIPPING):
    if dominating_B(min_val, max_val, min_actions, dominated, A, B) and B >= s:
        rows, cols = min_val.shape
        x = np.ones(shape = (len(min_actions) + 1)) / (len(min_actions) + 1)
        b = np.full((rows, 1), UPPER_BOUND)
        o = np.column_stack((max_val, b))
        f = min_val[:, B]
        e = o[A]
        xt = x.T
        if np.all(np.dot(o, xt) > f) and np.sum(x) <= 1:
            return np.dot(e, xt)
    return max_val[A][B] + 1

def SMAB(state, heuristic, alpha, beta, depth = MAX_DEPTH):
    if depth == 0 :
        evals= heuristic(state, state.player_1)
        return (evals, None)
    
    max_player = state.player_1
    min_player = state.player_2

    min_actions = state.promising_actions(min_player)
    max_actions = state.promising_actions(max_player)
    #shuffle(min_actions)
    #shuffle(max_actions)
    min_val = np.full((len(max_actions), len(min_actions)), alpha)
    max_val = np.full((len(max_actions), len(min_actions)), beta)

    dominated = is_dominated(min_val, max_val)
    
    for A in range(len(max_actions)):
        for B in range(len(min_actions)):
            if not dominated[A][B]:
                next_state = deepcopy(state)
                alpha_AB = min_val[A][B]
                beta_AB = max_val[A][B]

                p1, p2 = next_state.apply_action(max_actions[A], min_actions[B])
                next_state.update(p1, p2)
                if alpha_AB > beta_AB:
                    evals = SMAB(next_state, heuristic, alpha_AB, alpha_AB + E, depth - 1)[0]
                    if evals < alpha_AB:
                        dominated[A] = 1
                        print('row')
                    else:
                        dominated[:, B] = 1
                        print('col')
                else:
                    evals = SMAB(next_state, heuristic, alpha_AB, beta_AB, depth - 1)[0]
                    if evals < alpha_AB:
                        dominated[A] = 1
                        print('row')
                    elif evals > beta_AB:
                        dominated[:, B] = 1
                        print('col')
                    else:
                        min_val[A][B] = max_val[A][B] = evals

    res_dominated = np.where(dominated == 1)
    
    dominated_move_row = list(set([i[0] for i in list(zip(res_dominated[0]))]))
    dominated_move_actions = [max_actions[m] for m in dominated_move_row]

    for m in dominated_move_actions:
        max_actions.remove(m)
    min_val = np.delete(min_val, dominated_move_row, axis = 0)
    distribution, payoff = solve_game(min_val)
    best_action = max_actions[np.where(distribution == np.max(distribution))[0][0]]

    return payoff, best_action

def SMAB_v1(state, heuristic, alpha, beta, depth = MAX_DEPTH):
    if depth == 0 :
        evals= heuristic(state, state.player_1)
        return (evals, None)
    
    max_player = state.player_1
    min_player = state.player_2

    min_actions = state.promising_actions(min_player)
    max_actions = state.promising_actions(max_player)
    #shuffle(min_actions)
    #shuffle(max_actions)

    min_val = np.full((len(max_actions), len(min_actions)), alpha)
    max_val = np.full((len(max_actions), len(min_actions)), beta)

    dominated_row = list()
    dominated_col = list()
    
    for A in range(len(max_actions)):
        for B in range(len(min_actions)):
            if A not in dominated_row and B not in dominated_col:
                next_state = deepcopy(state)
                alpha_AB = cal_alpha_AB(min_val, max_val, max_actions, dominated_row, A, B)
                beta_AB = cal_beta_AB(min_val, max_val, min_actions, dominated_col, A, B)
                p1, p2 = next_state.apply_action(max_actions[A], min_actions[B])
                next_state.update(p1, p2)
                if alpha_AB > beta_AB:
                    evals = SMAB(next_state, heuristic, alpha_AB, alpha_AB + E, depth - 1)[0]
                    if evals < alpha_AB:
                        dominated_row.append(A)
                    else:
                        dominated_col.append(B)
                else:
                    evals = SMAB(next_state, heuristic, alpha_AB, beta_AB, depth - 1)[0]
                    if evals < alpha_AB:
                        dominated_row.append(A)
                    elif evals > beta_AB:
                        dominated_col.append(B)
                    else:
                        min_val[A][B] = max_val[A][B] = evals

    for m in dominated_row:
        max_actions.remove(m)
    min_val = np.delete(min_val, dominated_row, axis = 0)
    distribution, payoff = solve_game(min_val)
    best_action = max_actions[np.where(distribution == np.max(distribution))[0][0]]

    return payoff, best_action

def SMAB_cell_ordering(state, heuristic, alpha, beta, depth = MAX_DEPTH):
    if depth == 0 :
        evals = heuristic(state, state.player_1)
        return (evals, None)

    max_player = state.player_1
    min_player = state.player_2

    min_actions = state.promising_actions(min_player)
    max_actions = state.promising_actions(max_player)
    #shuffle(min_actions)
    #shuffle(max_actions)

    min_val = np.full((len(max_actions), len(min_actions)), alpha)
    max_val = np.full((len(max_actions), len(min_actions)), beta)

    dominated_row = list()
    dominated_col = list()
    ordering = list()
    for A in range(len(min_actions)):
        # Traversing Horizontally (cols)
        for j in range(A, len(min_actions)):
            if A < len(max_actions):
                ordering.append((A, j))
        # Traversing Vertically (rows)
        for i in range(A + 1, len(max_actions)):
                ordering.append((i, A))

    for (A, B) in ordering:
        if A not in dominated_row and B not in dominated_col:
            next_state = deepcopy(state)
            alpha_AB = cal_alpha_AB(min_val, max_val, max_actions, dominated_row, A, B)
            beta_AB = cal_beta_AB(min_val, max_val, min_actions, dominated_col, A, B)
            p1, p2 = next_state.apply_action(max_actions[A], min_actions[B])
            next_state.update(p1, p2)
            if alpha_AB > beta_AB:
                evals = SMAB_cell_ordering(next_state, heuristic, alpha_AB, alpha_AB + E, depth - 1)[0]
                if evals < alpha_AB:
                    dominated_row.append(A)
                else:
                    dominated_col.append(B)
            else:
                evals = SMAB_cell_ordering(next_state, heuristic, alpha_AB, beta_AB, depth - 1)[0]
                if evals < alpha_AB:
                    dominated_row.append(A)
                elif evals > beta_AB:
                    dominated_col.append(B)
                else:
                    min_val[A][B] = max_val[A][B] = evals

    for m in dominated_row:
        max_actions.remove(m)
    min_val = np.delete(min_val, dominated_row, axis = 0)
    distribution, payoff = solve_game(min_val)
    best_action = max_actions[np.where(distribution == np.max(distribution))[0][0]]

    return payoff, best_action
    
#++++++++++++++ DOUBLE ORACLE ++++++++++++++# (DEPRECATED)
"""
TOO HARD TO UNDERSTAND....
WHAT EVEN IS THIS
NOT EVEN SURE IF THIS IS WORKING
LIKE IT MEANT TO.
"""
def compute_NE(min_actions, max_actions, min_val, max_val):
    min_val = np.reshape(np.array(min_val), (len(max_actions), len(min_actions)))
    max_val = np.reshape(np.array(max_val), (len(max_actions), len(min_actions)))
    dist_1, payoff_1 = solve_game(min_val)
    dist_2, payoff_2 = solve_game(max_val)

    best_min = min_actions[np.where(dist_1 == np.max(dist_1))[0][0]]
    best_max = max_actions[np.where(dist_2 == np.max(dist_2))[0][0]]

    return (payoff_1 + payoff_2) / 2, dist_1.flatten(), dist_2.flatten()

def alpha_beta(state, heuristic, max_player, alpha, beta, depth):
    if depth == 0:
        evals = heuristic(state, state.player_1)
        return evals 
    # If max player, min player move first
    if max_player == state.player_1:
        if state.player_1 == 'upper':
            p1 = state.upper
        else: p1 = state.lower
        val = -inf
        p2_actions = state._actions(state.player_2)
        for action in p2_actions:
            next_state = deepcopy(state)
            p2 = next_state.read_move(action, state.player_2)
            for i in range(9):
                p2, p2 = next_state.check_piece(p2, p2)
                p1, p2 = next_state.check_piece(p1, p2)
            if next_state.player_1 == 'upper':
                next_state.upper = p1
                next_state.lower = p2
            else: 
                next_state.upper = p2
                next_state.lower = p1
            
            if depth % 2 == 0:
                next_state.turn += 1
                next_state._invincible()
                next_state.done = next_state.end_game()
            
            val = max(val, alpha_beta(next_state, heuristic, state.player_2, alpha, beta, depth - 1))
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return val
    # If min player, max player move first
    else:
        if state.player_1 == 'upper':
            p2 = state.lower
        else: p2 = state.upper
        val = +inf
        p1_actions = state._actions(state.player_1)
        for action in p1_actions:
            next_state = deepcopy(state)
            p1 = next_state.read_move(action, state.player_1)
            for i in range(9):
                p1, p1 = next_state.check_piece(p1, p1)
                p1, p2 = next_state.check_piece(p1, p2)
            if next_state.player_1 == 'upper':
                next_state.upper = p1
                next_state.lower = p2
            else:
                next_state.upper = p2
                next_state.lower = p1
            
            if depth % 2 == 0:
                next_state.turn += 1
                next_state._invincible()
                next_state.done = next_state.end_game()

            val = min(val, alpha_beta(next_state, heuristic, state.player_2, alpha, beta, depth - 1))
            beta = min(beta, val)
            if beta <= alpha:
                break
        return val

def double_oracle(state, heuristic, alpha, beta, depth): 
    if depth == 0:
        val = heuristic(state, state.player_1)
        return (val, None)
    min_AB = alpha_beta(state, heuristic, state.player_2, alpha, beta, depth*2)
    if alpha_beta(state, heuristic, state.player_1, alpha, beta, depth*2) == min_AB:
        return (min_AB, None)

    p1_act = state._actions(state.player_1)
    p2_act = state._actions(state.player_2)
    
    max_set = [choice(p1_act)]
    min_set = [choice(p2_act)]

    next_state = deepcopy(state)
    p1, p2 = next_state.apply_action(max_set[0], min_set[0])
    next_state.update(p1, p2)
    min_val = [alpha_beta(next_state, heuristic, state.player_2, alpha, beta, depth*2)]
    max_val = [alpha_beta(next_state, heuristic, state.player_1, alpha, beta, depth*2)]
    print("PASS THIS 1")
    while alpha <= beta:
        for x in range(len(max_set)):
            for y in range(len(min_set)):
                i = x + len(max_set)*y
                if min_val[i] < max_val[i]:
                    state_ij = deepcopy(state)
                    p1, p2 = state_ij.apply_action(max_set[0], min_set[0])
                    state_ij.update(p1, p2)
                    val, _ = double_oracle(state_ij, heuristic, min_val[i], max_val[i], depth - 1)
                    print("PASS THIS 2")
                    min_val[i] = max_val[i] = val
                val, max_dist, min_dist = compute_NE(min_set, max_set, min_val, max_val)
                (br_i, v_max) = BR_max(state, heuristic, alpha, beta, min_dist, depth)
                (br_j, v_min) = BR_max(state, heuristic, alpha, beta, max_dist, depth)
                print("PASS THIS 7")
                if br_i == None:
                    return alpha
                elif br_j == None:
                    return beta
                alpha = max(alpha, v_min)
                beta = min(beta, v_max)
                max_set.append(br_i)
                min_set.append(br_j)
    print("PASS THIS 8")
    return val, max_set

def BR_max(state, heuristic, alpha, beta, dist, depth):
    br_val = alpha
    br = None

    max_actions = state._actions(state.player_1)
    min_actions = state._actions(state.player_2)
    # Initialize pessimistic and optimistic bound
    min_val = np.zeros((len(max_actions), len(min_actions)))
    max_val = np.zeros((len(max_actions), len(min_actions)))
    
    for A in range(len(max_actions)):
        for B in range(len(min_actions)):
            next_state = deepcopy(state)
            p1, p2 = next_state.apply_action(max_actions[A], min_actions[B])
            next_state.update(p1, p2)

            min_val[A][B] = alpha_beta(next_state, heuristic, state.player_2, alpha, beta, depth*2)
            max_val[A][B] = alpha_beta(next_state, heuristic, state.player_1, alpha, beta, depth*2)
            print("PASS THIS 3")
            print(B)
            print(A)
            print(dist[B])
            print(min_val[A][B], max_val[A][B])
            if dist[B] > 0 and min_val[A][B] < max_val[A][B]:
                min_val_t = max(min_val[A][B], br_val - (sum(dist) - dist[B])*max_val[A][B])
                if min_val_t > max_val[A][B]:
                    continue
                else:
                    val, _ = double_oracle(next_state, heuristic, alpha, beta, depth - 1)
                    print("PASS THIS 4")
                    min_val[A][B] = max_val[A][B] = val 
            if sum(dist) * val >= br_val:
                br = max_actions[A]
                br_val = sum(dist) * val  
    return (br, br_val)

def BR_min(state, heuristic, alpha, beta, dist, depth):
    br_val = alpha
    br = None

    max_actions = state._actions(state.player_1)
    min_actions = state._actions(state.player_2)
    # Initialize pessimistic and optimistic bound
    min_val = np.zeros((len(max_actions), len(min_actions)))
    max_val = np.zeros((len(max_actions), len(min_actions)))

    for B in range(len(min_actions)):
        for A in range(len(max_actions)):
            next_state = deepcopy(state)
            p1, p2 = next_state.apply_action(max_actions[A], min_actions[B])
            next_state.update(p1, p2)

            min_val[A][B] = alpha_beta(next_state, heuristic, state.player_2, alpha, beta, depth*2)
            max_val[A][B] = alpha_beta(next_state, heuristic, state.player_1, alpha, beta, depth*2)
            print("PASS THIS 5")
            if dist[A] > 0 and min_val[A][B] < max_val[A][B]:
                min_val_t = max(min_val[A][B], br_val - (sum(dist) - dist[A])*max_val[A][B])
                if min_val_t > max_val[A][B]:
                    continue
                else:
                    val, _ = double_oracle(next_state, heuristic, alpha, beta, depth - 1)
                    print("PASS THIS 6")
                    min_val[A][B] = max_val[A][B] = val
            if sum(dist) * val >= br_val:
                br = max_actions[A]
                br_val = sum(dist) * val  
    return (br, br_val)

