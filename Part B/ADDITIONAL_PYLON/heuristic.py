from ADDITIONAL_PYLON.state import *
import numpy as np

UPPER_MID = [(4, -2)]
UPPER_LEFT_REGION = [(4, -4), (4, -3), (3,-4), (3,-3), (3, -2), (2,-4), (2, -3), (2, -2)]
UPPER_RIGHT_REGION = [(4, -1), (4, 0), (3, -1), (3, 0), (3, 1), (2, 0), (2, 1), (2, 2)]
MIDDLE_LEFT_REGION = [(1, -4), (1, -3), (1, -2), (0, -4), (0, -3), (0, -2), (-1, -3), (-1, -2), (-1, -1)]
CENTER_REGION = [(2, -1), (1, -1), (1, 0), (0, -1), (0, 0), (0, 1), (-1, 0), (-1, 1), (-2, 1)]
MIDDLE_RIGHT_REGION = [(1, 1), (1, 2), (1, 3), (0, 2), (0, 3), (0, 4), (-1, 2), (-1, 3), (-1, 4)]
LOWER_LEFT_REGION = [(-2, -2), (-2, -1), (-2, 0), (-3, -1), (-3, 0), (-3, 1), (-4, 0), (-4, 1)]
LOWER_RIGHT_REGION = [(-2, 2), (-2, 3), (-2, 4), (-3, 2), (-3, 3), (-3, 4), (-4, 3), (-4, 4)]
LOWER_MID = [(-4, 2)]

#++++++++++++ UTILITIES ++++++++++++#
def distance(coord1, coord2):
    (s, r1, q1) = coord1
    (s, r2, q2) = coord2
    return (abs(r1 - r2) + abs(q1 - q2) + abs(r1 - r2 + q1 - q2)) // 2

def overall_distance(pieces1, pieces2):
    dist = 0
    for p1 in pieces1:
        for p2 in pieces2:
            dist += distance(p1, p2)
    return dist

def player_set(game, player):
    if player == 'upper':
        region = UPPER_MID + UPPER_LEFT_REGION + UPPER_RIGHT_REGION
        return game.upper, game.lower, game.upper_throws, game.lower_throws, region
    else:
        region = LOWER_MID + LOWER_LEFT_REGION + LOWER_RIGHT_REGION
        return game.lower, game.upper, game.lower_throws, game.upper_throws, region

def check_region_advantage(region):
    score = 0
    if len(region['p1']) > len(region['p2']): score += 1
    elif len(region['p1']) < len(region['p2']): score -= 1
    p1 = {'r': 0, 'p': 0, 's': 0}
    p2 = {'r': 0, 'p': 0, 's': 0}

    for k, v in region.items():
        for token in v:
            if k == 'p1':
                p1[token[0]] += 1
            if k == 'p2':
                p2[token[0]] += 1

    for t1 in p1:
        if p2[WHAT_BEATS[t1]] > p1[t1]:
            score -= 1
        else:
            score += 1

    return score

#++++++++++++ FEATURES ++++++++++++#
def defend(game, player):
    """
    Idea: If each token are close together it may be said that it is easier to defend each other
    and if the tokens doesnt go past the opponent's region we have more defend power. Having more
    throws than the opponent have significant defensive power, as we can just stomp them if they
    come to our throw region.
    Measures the current state defend power.
    - If each token piece is in defensive region increase score by 1 else -1
    - If the distance between token does not pass the threshold increase score by 1 else -1.
    - If player's throw is larger than opponent, higher defend power.
    """
    pass

def attack(game, player):
    """
    The idea is to check each region player 1 and player 2 tokens. If in a region either player
    has more tokens than the other and their token can beat the other, then the player can be said
    to have advantage over the player in that region.
    If player 1 has 1 rock and 1 paper token in a region and player 2 has 1 scissor token, then
    player 1 has overall advantage in that region. If both player have the same tokens symbol,
    then both player has no advantage over each other.
    The more advantage over the whole region, it can be said that it has more attack power than the other.
    """
    pass

def retreat(game, player):
    """
    The idea is to run back from opposing tokens when we have a disadvantage. or even gather
    together. To defend each other.
    """
    pass

def cost_to_enemy(game, player):
    player_1, player_2, p1_throw, p2_throw, _ = player_set(game, player)

    dist = []
    for p1 in player_1:
        for p2 in player_2:
            if WHAT_BEATS[p2[0]] == p1[0]:
                dist.append((p1, p2, distance(p1, p2)))
    dist = np.array(dist)

    shortest_dist = {}
    for i in dist:
        if i[0] not in shortest_dist:
            shortest_dist[i[0]] = [i[-1], i[1]]
        elif i[0] in shortest_dist:
            if shortest_dist[i[0]][0] > i[-1]:
                shortest_dist[i[0]] = [i[-1], i[1]]
    total_distance = 0
    for short in shortest_dist.values():
        total_distance += short[0]
    if total_distance:
        return (9 - (total_distance / len(shortest_dist))) * 100 / 9
    return 0

def total_tokens(game, player):
    player_1, player_2, p1_throw, p2_throw, _ = player_set(game, player)

    total_tokens = len(player_1) + p1_throw
    return (total_tokens) * 100 / NO_OF_TOKEN

def cost_from_enemy(game, player):
    player_1, player_2, p1_throw, p2_throw, _ = player_set(game, player)

    dist = []
    for p1 in player_1:
        for p2 in player_2:
            if WHAT_BEATS[p1[0]] == p2[0]:
                dist.append((p1, p2, distance(p1, p2)))
    dist = np.array(dist)
    shortest_dist = {}
    for i in dist:
        if i[0] not in shortest_dist:
            shortest_dist[i[0]] = [i[-1], i[1]]
        elif i[0] in shortest_dist:
            if shortest_dist[i[0]][0] > i[-1]:
                shortest_dist[i[0]] = [i[-1], i[1]]
    total_distance = 0
    for short in shortest_dist.values():
        total_distance += short[0]
    if total_distance:
        return (total_distance / len(shortest_dist)) * 100 / 9
    return 0

def save_throws(game, player):
    player_1, player_2, p1_throws, p2_throws, _ = player_set(game, player)

    return (p1_throws) * 100 / NO_OF_TOKEN

def enemy_captured(game, player):
    player_1, player_2, p1_throws, p2_throws, _ = player_set(game, player)
    return (NO_OF_TOKEN - len(player_2) - p2_throws) * 100 / 9

def cost_to_allies(game, player):
    player_1, player_2, p1_throws, p2_throws, _ = player_set(game, player)

    dist = []
    for p1 in player_1:
        for p2 in player_1:
            if WHAT_BEATS[p2[0]] == p1[0]:
                dist.append((p1, p2, distance(p1, p2)))
    dist = np.array(dist)
    shortest_dist = {}
    for i in dist:
        if i[0] not in shortest_dist:
            shortest_dist[i[0]] = [i[-1], i[1]]
        elif i[0] in shortest_dist:
            if shortest_dist[i[0]][0] > i[-1]:
                shortest_dist[i[0]] = [i[-1], i[1]]
    total_distance = 0
    for short in shortest_dist.values():
        total_distance += short[0]
    if total_distance:
        return (8 - (total_distance / len(shortest_dist))) * 100 / 8
    return 0

#++++++++++++ EVALUATION ++++++++++++#
def mid_game(game, player):

    f1 = cost_to_enemy(game, player)
    f2 = cost_from_enemy(game, player)
    f3 = total_tokens(game, player)
    f4 = save_throws(game, player)
    f5 = enemy_captured(game, player)
    f6 = cost_to_allies(game, player)
    return (f1*20 + f2*10 + f3*20 + f4*0 + f5*20 + f6 * 0)

def greedy(game, player):
    f1 = cost_to_enemy(game, player)
    f2 = cost_from_enemy(game, player)
    f3 = total_tokens(game, player)
    f4 = save_throws(game, player)
    f5 = enemy_captured(game, player)
    return (f1*15 + f2*12 + f3*15 + f4*1 + f5*15)

#++++++++++++ DEPRECATED ++++++++++++#

def targeted_throw(game, player):
    player_1, player_2, p1_throws, p2_throws, _ = player_set(game, player)
    in_region = []
    for token2 in player_2:
        (s, r, q) = token2
        if r >= p1_throws - 5:
            in_region.append(token2)
    dist = []
    for r1 in in_region:
        for p2 in player_2:
            if WHAT_BEATS[p2[0]] == r1[0]:
                dist.append((r1, p2, distance(r1, p2)))
    shortest_dist = {}
    for i in dist:
        if i[0] not in shortest_dist:
            shortest_dist[i[0]] = [i[-1], i[1]]
        elif i[0] in shortest_dist:
            if shortest_dist[i[0]][0] > i[-1]:
                shortest_dist[i[0]] = [i[-1], i[1]]
    if shortest_dist:
        best_throw = [0, None]
        for token in shortest_dist:
            if shortest_dist[token][0] > best_throw[0] and shortest_dist[token][0] > 2 :
                best_throw = [shortest_dist[token][0], token]

        if best_throw[1]:
            token = best_throw[1]
            action = ("THROW", WHAT_BEATS[token[0]], (token[1], token[2]))
            return action
    return 0
