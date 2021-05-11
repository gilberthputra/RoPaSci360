import random

symbols = ("r", "p", "s")
BEATS_WHAT = {'r': 's', 'p': 'r', 's': 'p'}
WHAT_BEATS = {'r': 'p', 'p': 's', 's': 'r'}
MAX_TURNS = 360
UPPER_BOUND = +4
LOWER_BOUND = -4
BOUNDS = range(LOWER_BOUND, UPPER_BOUND+1)
grid = [(r, q) for r in BOUNDS for q in BOUNDS if -r-q in BOUNDS]

class Player:
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        # put your code here
        self.player = player

        self.own = {"r":[], "s":[], "p":[]}
        self.opp = {"r":[], "s":[], "p":[]}

        self.own_throws = 9
        self.opp_throws = 9

        self.turn_number = 0

        self.stance = "neutral"
        self.target = None

    #This function is to calculate the distance between position 1 and 2
    #Implemented from (redblobgames.com/grids/hexagons/#distances).
    def hex_distance(self, pos1, pos2):
        return (abs(pos1[1] - pos2[1]) + abs(pos1[1] + pos1[0] - pos2[1] - pos2[0]) + abs(pos1[0] - pos2[0]))/2

    def inbound(self, location):
        (r, q) = location
        if abs(r) > UPPER_BOUND or abs(q) > UPPER_BOUND:
            return False

        list = [(4, 1), (4, 2), (4, 3), (4, 4), (3, 2),
                (3, 3), (3, 4), (2, 3), (2, 4), (1, 4),
                (-1, -4), (-2, -4), (-2, -3), (-3, -4), (-3, -3),
                (-3, -2), (-4, -4), (-4, -3), (-4, -2), (-4, -1)]

        return location not in list

    def neighbours(self, location):
        (r, q) = location
        ## Neighbours in order of Top-Left, Top-Right, Mid-Left, Mid-Right,
        ## Bottom-Left, Bottom-Right
        neighbours = [(r + 1, q - 1), (r + 1, q),
                      (r, q - 1), (r, q + 1),
                      (r - 1, q), (r - 1, q + 1)]

        results = filter(self.inbound, neighbours)
        return list(results)

    def find_opp_invincible(self):
        inv = []
        if len(self.opp["r"]) > 0 and len(self.own["p"]) == 0:
            inv.append("r")
        if len(self.opp["p"]) > 0 and len(self.own["s"]) == 0:
            inv.append("p")
        if len(self.opp["s"]) > 0 and len(self.own["r"]) == 0:
            inv.append("s")
        return inv

    def find_own_invincible(self):
        inv = []
        if len(self.own["r"]) > 0 and len(self.opp["p"]) == 0:
            inv.append("r")
        if len(self.own["p"]) > 0 and len(self.opp["s"]) == 0:
            inv.append("p")
        if len(self.own["s"]) > 0 and len(self.opp["r"]) == 0:
            inv.append("s")
        return inv

    def tokens_remaining(self, token_dict):
        sum = 0
        for symbol in token_dict:
            sum += len(symbol)
        return sum

    def all_tokens(self, token_dict):
        all = []
        for symbol in token_dict:
            all.extend(token_dict[symbol])
        return all

    def slide_options(self, token):
        """
        Input: token
        Output: ["SLIDE", before, after]
        """
        (r, q) = token
        before = (r, q)
        nbr = self.neighbours(before)
        return [("SLIDE", before, after) for after in nbr]

    def swing_options(self, token):
        """
        Input: token
        Output: ["SWING", before, after]
        """
        (r, q) = token
        before = (r, q)
        nbr = self.neighbours(before)

        pivot = []
        for n in nbr:
            [x, y] = n
            for symbol in self.own:
                if [x, y] in self.own[symbol]:
                    pivot.append(n)
        pivot_nbr = []
        for p in pivot:
            (x, y) = p
            for n in self.neighbours(p):
                if n != (r, q) and n not in nbr:
                    pivot_nbr.append(("SWING", before, n))
        pivot_nbr = list(dict.fromkeys(pivot_nbr))
        return pivot_nbr

    def throw_options(self, symbol):
        throwable = []
        if self.player == "upper":
            for coord in grid:
                if coord[0] >= (self.own_throws - 5):
                    throwable.append(("THROW", symbol, coord))
        else:
            for coord in grid:
                if coord[0] <= -(self.own_throws - 5):
                    throwable.append(("THROW", symbol, coord))
        return throwable

    #Symbol is the type of tokens I want the neighbours for
    def get_all_neighbours(self, symbol):
        all_neigh = []
        for token in self.own[symbol]:
            all_neigh.extend(self.neighbours(token))
        return all_neigh
    
    """
    def throw_defensively(self, symbol):
        if self.player == "upper":
            pass
    """

    def move_to(self, position, target):
        moves = []
        moves.extend(self.slide_options(position))
        moves.extend(self.swing_options(position))

        least_distance = 99
        best_move = moves[0]
        all = self.all_tokens(self.own)
        for move in moves:
            if move[2] not in all:
                dist = self.hex_distance(move[2], target)
                if dist < least_distance:
                    best_move = move
                    least_distance = dist
        return best_move

    def most_endangered(self):
        endangered = []

        least_distance = 99
        endangered_symbol = None
        endangered_token = None
        for symbol in self.own:
            for token1 in self.own[symbol]:
                for token2 in self.opp[WHAT_BEATS[symbol]]:
                    dist = self.hex_distance(token1, token2)
                    if dist < least_distance:
                        endangered_symbol = symbol
                        endangered_token = token1
                        least_distance = dist
        endangered.append(least_distance)
        endangered.append(endangered_symbol)
        endangered.append(endangered_token)
        return endangered

    def best_ally(self, symbol, position):
        ally = []
        least_distance = 99
        ally_symbol = None
        ally_token = None
        if len(self.own[BEATS_WHAT[symbol]]) > 0:
            for token in self.own[BEATS_WHAT[symbol]]:
                dist = self.hex_distance(position, token)
                if dist < least_distance:
                    ally_symbol = BEATS_WHAT[symbol]
                    ally_token = token
                    least_distance = dist
        elif self.tokens_remaining(self.own) > 0:
            for sym in self.own:
                for token in self.own[sym]:
                    dist = self.hex_distance(position, token)
                    if dist < least_distance:
                        ally_symbol = sym
                        ally_token = token
                        least_distance = dist
        else:
            return None
        ally.append(ally_symbol)
        ally.append(ally_token)
        return ally

    def most_aggro(self):
        aggro = []

        least_distance = 99
        aggro_symbol = None
        aggro_token = None
        aggro_token_target = None
        for symbol in self.own:
            for token1 in self.own[symbol]:
                for token2 in self.opp[BEATS_WHAT[symbol]]:
                    dist = self.hex_distance(token1, token2)
                    if dist < least_distance:
                        aggro_symbol = symbol
                        aggro_token = token1
                        aggro_token_target = token2 
                        least_distance = dist
        aggro.append(least_distance)
        aggro.append(aggro_symbol)
        aggro.append(aggro_token)
        aggro.append(aggro_token_target)
        return aggro

    def throw_closest(self, symbol, position):
        throwable = []
        options = self.throw_options(symbol)
        allies = self.all_tokens(self.own)

        for token in self.neighbours(position):
            throw = ("THROW", symbol, token)
            if throw in options and token not in allies:
                throwable.append(throw)
        if len(throwable) > 0:
            return random.choice(throwable)
        
        least_dist = 99
        best_opt = None
        for option in options:
            if option[2] not in allies:
                dist = self.hex_distance(option[2], position)
                if dist < least_dist:
                    best_opt = option
                    least_dist = dist
        return best_opt

    def throw_middle(self, symbol):
        options = self.throw_options(symbol)
        allies = self.all_tokens(self.own)
        least_dist = 99
        best_opt = None
        for option in options:
            if option[2] not in allies:
                dist = self.hex_distance(option[2], (0, 0))
                if dist < least_dist:
                    best_opt = option
                    least_dist = dist
        return best_opt

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here

        #If it's the start of the game throw a random token in the middle of the first throw
        if self.own_throws == 9:
            if self.player == "upper":
                #throw(random.choice(tokens), [4,-2])
                return ("THROW", random.choice(symbols), (4, -2))
            else:
                #throw(random.choice(tokens), [-4,2])
                return ("THROW", random.choice(symbols), (-4, 2))

        inv = self.find_opp_invincible()
        if len(inv) > 0 and self.own_throws > 0:
            choice = random.choice(inv)
            endangered = self.most_endangered()
            if self.tokens_remaining(self.own) > 0 and endangered[0] != 99:
                return self.throw_closest(WHAT_BEATS[choice], endangered[2])
            else:
                return self.throw_middle(WHAT_BEATS[choice])

        if self.tokens_remaining(self.own) == 0 and self.own_throws > 0:
            if self.tokens_remaining(self.opp) > 0:
                sym = random.choice(self.find_opp_invincible())
                return self.throw_middle(sym)
            else:
                return self.throw_middle(random.choice(symbols))

        if self.target != None:
            return self.move_to(self.own[WHAT_BEATS[self.target]][0], self.opp[self.target][0])

        endangered = self.most_endangered()
        ally = self.best_ally(endangered[1], endangered[2])
        aggro = self.most_aggro()

        if self.stance == "neutral":
            if endangered[0] <= aggro[0]:
                if ally == None and self.own_throws > 0:
                    return self.throw_closest(BEATS_WHAT[endangered[1]], endangered[2])
                else:
                    return self.move_to(endangered[2], random.choice(self.neighbours(ally[1])))
            else:
                return self.move_to(aggro[2], aggro[3])
        elif self.stance == "defensive":
            if ally == None and self.own_throws > 0:
                return self.throw_closest(BEATS_WHAT[endangered[1]], endangered[2])
            else:
                return self.move_to(endangered[2], random.choice(self.neighbours(ally[1])))
        else:
            return self.move_to(aggro[2], aggro[3])
            
        
    #def throw(self, player, action):
    #    if player == "opponent":
    #        self.opp[opponent_action[1]].append(list(opponent_action[2]))
    #    else:


    #def move(self, player, action):
    #    for hex in self.own[token]:
    #        if curr_hex == hex:
    #            hex[0] = next_hex[0]
    #            hex[1] = next_hex[1]
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # put your code here

        self.target = None
        
        #Opponent's throws are executed here
        if opponent_action[0] == "THROW":
            self.opp[opponent_action[1]].append(list(opponent_action[2]))
            self.opp_throws -= 1
        #Oppenent's slides and swings are executed here
        else:
            for key in self.opp:
                for hex in self.opp[key]:
                    if hex == list(opponent_action[1]):
                        hex[0] = opponent_action[2][0]
                        hex[1] = opponent_action[2][1]

        #Player's throws are executed here
        if player_action[0] == "THROW":
            self.own[player_action[1]].append(list(player_action[2]))
            self.own_throws -= 1
        #Player's slides and swings are executed here
        else:
            for key in self.own:
                for hex in self.own[key]:
                    if hex == list(player_action[1]):
                        hex[0] = player_action[2][0]
                        hex[1] = player_action[2][1]

        #then delete the ones that die
        to_delete = []

        for symbol in self.opp:
            for token1 in self.opp[symbol]:
                for token2 in self.opp[BEATS_WHAT[symbol]]:
                    if token1 == token2:
                        to_delete.append(("opp", BEATS_WHAT[symbol], token2))
                for token2 in self.own[BEATS_WHAT[symbol]]:
                    if token1 == token2:
                        to_delete.append(("own", BEATS_WHAT[symbol], token2))

        for symbol in self.own:
            for token1 in self.own[symbol]:
                for token2 in self.opp[BEATS_WHAT[symbol]]:
                    if token1 == token2:
                        to_delete.append(("opp", BEATS_WHAT[symbol], token2))
                for token2 in self.own[BEATS_WHAT[symbol]]:
                    if token1 == token2:
                        to_delete.append(("own", BEATS_WHAT[symbol], token2))

        print(to_delete)
        #to_delete = list(dict.fromkeys(to_delete))
        for token in to_delete:
            if token[0] == "opp":
                if token[2] in self.opp[token[1]]:
                    self.opp[token[1]].remove(token[2])
            else:
                if token[2] in self.own[token[1]]:
                    self.own[token[1]].remove(token[2])

        to_delete.clear()

        #if opponent_action[0] == "THROW":
        
        #check if the token dies
        #for token in self.opp[WHAT_BEATS[opponent_action[1]]]:
        #    if token == opponent_action[2]:
        #        to_delete.append(("opp", opponent_action[1], opponent_action[2]))
        #for token in self.own[WHAT_BEATS[opponent_action[1]]]:
        #    if token == opponent_action[2]:
        #        to_delete.append(("opp", opponent_action[1], opponent_action[2]))
        #check if the token kills anything
        #for token in self.opp[BEATS_WHAT[opponent_action[1]]]:
        #    if token == opponent_action[2]:
        #       to_delete.append(("opp", BEATS_WHAT[opponent_action[1]], opponent_action[2]))
        #for token in self.own[BEATS_WHAT[opponent_action[1]]]:
        #    if token == opponent_action[2]:
        #        to_delete.append(("own", BEATS_WHAT[opponent_action[1]], opponent_action[2]))


        #increment turn
        self.turn_number += 1

        opp_number = self.tokens_remaining(self.opp)
        own_number = self.tokens_remaining(self.own)

        #Changing state
        if opp_number == own_number:
            if self.turn_number < 300:
                if self.opp_throws == self.own_throws:
                    self.stance = "neutral"
                elif self.opp_throws > self.own_throws:
                    self.stance = "defensive"
                else:
                    self.stance = "aggressive"
            else:
                self.stance = "aggressive"
        elif opp_number > own_number:
            self.stance = "defensive"
        else:
            self.stance = "aggressive"

        inv = self.find_own_invincible()
        if len(inv) > 0:
            for symbol in inv:
                if len(self.opp[BEATS_WHAT[symbol]]) > 0:
                    self.target = BEATS_WHAT[symbol]
                else:
                    self.target = None

#Strats
#group them together in a line or other structure
#then encircle a token?
#prefer to stay in throwing range, easier to attack and defend, harder for opponent to attack and defend
#try to expand throwing range quickly maybe?
#tokens can either attack or defend
#could try and close distance to opponents to attack and get in the way of opponents trying to attack
#or could just group up together and not bother attacking

#only need to perform basic pathfinding searches?
#determine which token gets to move with a heuristic of atk/def

#tokens run away to a token that can defend them, or plop one down behind them