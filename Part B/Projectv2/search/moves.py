import search.classes

def slide(graph, token):
    symbol = token[0]
    lctn = token[1]
    nbr = graph.neighbours(lctn)
    return [(symbol, i) for i in nbr if graph.rules(symbol, i)]

def swing(graph, token, player):
    symbol = token[0]
    lctn = tuple(token[1])
    nbr = graph.neighbours(lctn)
    pivot = []

    for n in nbr:
        if player == 'upper':
            tmp = graph.upper['r'] + graph.upper['s'] + graph.upper['p']
        elif player == 'lower':
            tmp = graph.lower['r'] + graph.lower['s'] + graph.lower['p']
        if n in tmp:
            pivot.append(n)

    pivot_nbr = [(symbol, n) for p in pivot for n in graph.neighbours(p) \
                if n != lctn and n not in nbr]
    pivot_nbr = list(dict.fromkeys(pivot_nbr))

    return pivot_nbr

def possible_actions(graph, token, player):

    if player is None:
        player = 'upper'

    results = []
    results.extend([(i[0], i[1], 'slide') for i in slide(graph, token)])
    results.extend([(i[0], i[1], 'swing') for i in swing(graph, token, player)])

    return results

def apply_action(graph, action, player):

    for move in action:
        print(move)
