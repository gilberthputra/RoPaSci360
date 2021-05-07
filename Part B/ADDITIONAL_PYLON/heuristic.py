from state import *

def advantage(game, player):
    if player == 'upper':
        p1 = game.upper
        p2 = game.lower
        p1_throw = game.upper_throws
        p2_throw = game.lower_throws
    elif player == 'lower':
        p1 = game.lower
        p2 = game.upper
        p1_throw = game.lower_throws
        p2_throw = game.upper_throws

    captured_by_player = NO_OF_TOKEN - len(p2) - p2_throw
    got_captured = NO_OF_TOKEN - len(p1) - p1_throw

    if captured_by_player > got_captured:
        score = 10
    elif captured_by_player == got_captured:
        score = 0
    else:
        score = -10

    return score

def vulnerable(game, player):
    if player == 'upper':
        p1 = game.upper
        p2 = game.lower
        p1_throw = game.upper_throws
        p2_throw = game.lower_throws
    elif player == 'lower':
        p1 = game.lower
        p2 = game.upper
        p1_throw = game.lower_throws
        p2_throw = game.upper_throws

    p1_s = {'r': 0, 'p': 0, 's':0}
    for p in p1:
        p1_s[p[0]] += 1
    p2_s = {'r': 0, 'p': 0, 's':0}
    for p in p2:
        p2_s[p[0]] += 1
    
    score = 0
    for s in p1_s:
        if p2_s[WHAT_BEATS[s]] > p1_s[s] and p1_throw < p2_throw:
            score -= 10
        else:
            score += 10
    
    return score

def defend(game, player): pass
    """
    The idea is to not move tokens out of throw zone, because that will made it to be harder
    to defend. When opponent total tokens are equal to player tokens.
    """

def attack(game, player): pass
    """
    The idea is to be aggressive when opponent total tokens is less than player tokens.
    Go out of the throw zone and just chase enemies down.
    """

def run(game, player): pass
    """
    The idea is to run back from opposing tokens when we have a disadvantage. or even gather
    together. To defend each other.
    """

def mid_game(game, player):
    ad = advantage(game, player) * 1.5
    vu = vulnerable(game, player) * -2
    print('ad', ad)
    print('vu', vu)
    return ad + vu