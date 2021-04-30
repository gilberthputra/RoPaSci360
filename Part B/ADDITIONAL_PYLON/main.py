from ropasci_game import *

def main():
    g = RoPaSci360()
    board = g.new_board()

    board[2, 6] = ROCK
    board[8, 8] = SCISSOR.lower()
    board[7, 7] = SCISSOR.lower()
    g.board = board
    print(board)
    upper = g.get_upper()
    lower = g.get_lower()
    g.lower_throws = 0
    for i in lower:
        print(g.check_throw(('s', 5, -4), 'Lower'))
main()
