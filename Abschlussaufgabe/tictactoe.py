#create tic tac toe board
import numpy as np
import random
def create_board():
    board = np.zeros((3,3), dtype=int)
    return board
board = create_board()
board
#place marker on board
def place(board, player, position):
    if board[position] == 0:
        board[position] = player
#check for win
def possibilities(board):
    l = []
    for i in range(len(board)):
        for j in range(len(board)):
            if board[i][j] == 0:
                l.append((i,j))
    return l
def random_place(board, player):
    selection = possibilities(board)
    current_loc = random.choice(selection)
    place(board, player, current_loc)
    return board
def row_win(board, player):

    for x in range(len(board)):
        win = True

        for y in range(len(board)):
            if board[x, y] != player:
                win = False
                continue

        if win == True:
            return(win)
    return(win)
def col_win(board, player):
    
        for x in range(len(board)):
            win = True
    
            for y in range(len(board)):
                if board[y][x] != player:
                    win = False
                    continue
    
            if win == True:
                return(win)
        return(win)
def diag_win(board, player):
    win = True
    for x in range(len(board)):
        if board[x, x] != player:
            win = False
    if win == True:
        return win
    win = True
    for x in range(len(board)):
        if board[x, 2 - x] != player:
            win = False
    return win
def evaluate(board):
    winner = 0

    for player in [1, 2]:
        if (row_win(board, player) or
            col_win(board,player) or
            diag_win(board,player)):
            
            winner = player

    if np.all(board != 0) and winner == 0:
        winner = -1
    return winner
def play_game():
    board, winner, counter = create_board(), 0, 1
    print(board)
    while winner == 0:
        for player in [1, 2]:
            random_place(board, player)
            print("Board after " + str(counter) + " move")
            print(board)
            counter += 1
            winner = evaluate(board)
            if winner != 0:
                break
    return winner
play_game()
# Path: Abschlussaufgabe/tictactoe.py


