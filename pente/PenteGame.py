from __future__ import print_function
import sys
sys.path.append('..')
from Game import Game
import numpy as np
import copy

"""
Game class implementation for the game of Pente.
Based on the OthelloGame then getGameEnded() was adapted to new rules.

Author: Evgeny Tyurin, github.com/evg-tyurin
Date: Jan 5, 2018.

Based on the OthelloGame by Surag Nair.
"""
class PenteGame(Game):
    def __init__(self, n=9):
        self.n = 9

    def getActionSize(self):
        return 81 + 1

    def getInitBoard(self):
        # board = [[0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0,0]]
        board = np.zeros((9, 9))
        return board #(board, 0, 0)

    def getNextState(self, game_state, player, action):
        return (add_stone(game_state, player, action), opponent(player))

    def getGameEnded(self, board, player):
        # (board, p1_captures, p2_captures) = game_state
        # return p1_captures >= 10 or p2_captures >= 10 or five(game_state[0])
        return five(board) != 0

    def getCanonicalForm(self, board, player):
        # return state if player==1, else return -state if player==-1
        # (board, p1_captures, p2_captures) = game_state
        if player == 1:
            return board
        # return (-1 * board, p2_captures, p1_captures)
        return -1 * board

    def getValidMoves(self, board, player):
        # (board, p1_captures, p2_captures) = game_state
        # return a fixed size binary vector
        valids = [0]*self.getActionSize()
        any_valid = False
        for i in range(len(board)):
            for j in range(len(board[0])):
                if board[i][j] == 0:
                    any_valid = True
                    valids[9 * i + j] = 1
        if not any_valid:
            return np.array([0]*self.getActionSize())
        return np.array(valids)

    def getSymmetries(self, board, pi):
        # (board, p1_captures, p2_captures) = game_state
        # mirror, rotational
        assert(len(pi) == self.n**2+1)  # 1 for pass
        pi_board = np.reshape(pi[:-1], (9, 9))
        l = []

        for i in range(1, 5):
            for j in [True, False]:
                newB = np.rot90(board, i)#, p1_captures, p2_captures)
                newPi = np.rot90(pi_board, i)
                if j:
                    newB = np.fliplr(newB)#, p2_captures, p1_captures)
                    newPi = np.fliplr(newPi)
                l += [(newB, list(newPi.ravel()) + [pi[-1]])]
        return l

    def stringRepresentation(self, board):
        # 8x8 numpy array (canonical board)
        return str(board)


def display(board):
    # (board, p1_captures, p2_captures) = game_state
    n = board.shape[0]

    print("   ", end="")
    for y in range(n):
        print (y,"", end="")
    print("")
    print("  ", end="")
    for _ in range(n):
        print ("-", end="-")
    print("--")
    for y in range(n):
        print(y, "|",end="")    # print the row #
        for x in range(n):
            piece = board[y][x]    # get the piece to print
            if piece == -1: print("X ",end="")
            elif piece == 1: print("O ",end="")
            else:
                if x==n:
                    print("-",end="")
                else:
                    print("- ",end="")
        print("|")

    print("  ", end="")
    for _ in range(n):
        print ("-", end="-")
    print("--")

def flipped(board):
    def row_flipped(row):
        return [-1 * x for x in row]
    return np.array([row_flipped(row) for row in board])

def five(board, seed=None):
    found = 0
    deltas = [(0, 1), (1, 0), (1, 1)]
    for i in range(len(board)):
        for j in range(len(board[0])):
            for delta in deltas:
                if check_towards(i, j, board, delta, 1) > 0:
                    return 1
                if check_towards(i, j, board, delta, -1) > 0:
                    return -1
    return 0

def check_towards(i, j, board, delta, player):
    (dx, dy) = delta
    if is_valid(board, (i + 4 * dx, j + 4 * dy)):
        for k in range(1, 5):
            if board[i + k*dx][j + k*dy] != player:
                return 0
        return 1
    return 0

def removals(board, stone, pos, diff):
    one = sum(pos, diff)
    two = sum(one, diff)
    three = sum(two, diff)
    if not is_valid(board, three):
        return []
    if stone_at(board, one) == opponent(stone) and stone_at(board, two) == opponent(stone) and stone_at(board, three) == stone:
        return [one, two]
    return []

def add_stone(board, stone, pos):
    # (board, p1_captured, p2_captured) = game_state
    out = copy.deepcopy(board)
    # print("raw_pos: {0}".format(pos))
    pos = (int(pos / 9), int(pos) % 9)
    # print("pos: {0}".format(pos))
    out[pos[0]][pos[1]] = stone
    to_remove = removals(board, stone, pos, (-1, 0)) + \
        removals(board, stone, pos, (1, 0)) + \
        removals(board, stone, pos, (0, -1)) + \
        removals(board, stone, pos, (0, 1)) + \
        removals(board, stone, pos, (1, 1)) + \
        removals(board, stone, pos, (1, -1)) + \
        removals(board, stone, pos, (-1, 1)) + \
        removals(board, stone, pos, (-1, -1))
    for p in to_remove:
        out[p[0]][p[1]] = stone
        # if stone == 1:
        #     p1_captured += 1
        # else:
        #     p2_captured += 1
    # print("updated: {0}".format(out))
    return out #(out, p1_captured, p2_captured)

def stone_at(board, pos):
    return board[pos[0]][pos[1]]

def opponent(stone):
    if stone == 1:
        return -1
    return 1

def sum(pos, dpos):
    return (pos[0] + dpos[0], pos[1] + dpos[1])

def is_valid(board, pos):
    return pos[0] >= 0 and pos[0] < len(board) and pos[1] >= 0 and pos[1] < len(board[0])

def valid_move(board, pos):
    return is_valid(board, pos) and stone_at(board, pos) == 0
