"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    count_X = 0
    count_O = 0
    for row in board:
        for element in row:
            if element == X:
                count_X += 1
            elif element == O:
                count_O += 1

    if count_X == 0 and count_O == 0:
        return X
    if count_X>count_O:
        return O
    return X

def actions(board):
    action = []
    for i in range(3):
        for j in range(3):
            if board[i][j] == None:
                action.append((i,j))
    return action


def result(board, action):
    i = action[0]
    j = action[1]
    if i>2 or i<0:
        raise ValueError 

    if j>2 or j<0:
        raise ValueError

    move = player(board)
    new_board = copy.deepcopy(board)
    new_board[i][j] = move

    return new_board


def win(board,c):

    for i in range(3):
        if board[i][0] == c and board[i][1] == c and board[i][2] == c:
            return True
        if board[0][i] == c and board[1][i] == c and board[2][i] == c:
            return True


    if board[0][0] == c and board[1][1] == c and board[2][2]==c:
        return True

    if board[0][2] == c and board[1][1] == c and board[2][0]==c:
        return True

    return False


def winner(board):
    if win(board,X):
        return X
    if win(board,O):
        return O

    return None



def terminal(board):
    action = actions(board)
    if winner(board) != None or len(action)==0:
        return True
    return False


def utility(board):
    winner = winner(board)
    if winner == X:
        return 1
    elif winner == O:
        return -1
    return 0


def calculate(board):
    action = actions(board)
    play = player(board)
    win = winner(board)
    if win == X:
        return 1,-1,-1
    elif win == O:
        return -1,-1,-1
    elif terminal(board):
        return 0,-1,-1

    r = -1
    c = -1  
    if play == X:
        val = -2
        cur = -2
        for act in action:
            score,x,y = calculate(result(board,act))
            cur = max(cur,score)
            if cur>val:
                val = cur
                r = act[0]
                c = act[1]

    else:
        val = 2
        cur = 2
        for act in action:
            score,x,y = calculate(result(board,act))
            cur = min(cur,score)
            if cur<val:
                val = cur
                r = act[0]
                c = act[1]

    return val,r,c

def minimax(board):

    if terminal(board):
        return None
    score,x,y = calculate(board)
    final = (x,y)
    return final
