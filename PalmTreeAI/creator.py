import pickle
import chess
import chess.pgn
import os
import sys
import random
import chess.svg
import numpy as np
import tensorflow as tnsr
from tensorflow.keras import layers


sys.setrecursionlimit(0x100000)
class pair:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class dataPool:
    def __init__(self, path):
        self.path = path
        self.white = []
        self.black = []
        self.openings = []
        self.gatherData()

    def gatherData(self):
        # creates database based on folder of pgns
        for file in os.listdir(self.path):
            print("reading " + file)
            if (file.endswith('pgn')):
                pgn = open(os.path.join(self.path, file))
                game = chess.pgn.read_game(pgn)
                while game is not None:
                    i = 0
                    result = game.headers['Result'].strip()
                    if result == '1-0':
                        self.getGameData(game, 1)
                    elif result == '0-1':
                        self.getGameData(game, 0)
                    else:
                        self.getGameData(game, 1)
                        self.getGameData(game, 0)
                    try:
                        game = chess.pgn.read_game(pgn)
                    except:
                        game = chess.pgn.read_game(pgn)


    def getGameData(self, game, whiteOrBlack):
        iter = 0
        board = chess.Board()
        if whiteOrBlack:
            for move in game.mainline_moves():
                if iter % 2 != 0:
                    board.push(move)
                    iter += 1
                    continue
                if not iter:
                    iter += 1
                    self.openings.append(move)
                key = board
                board.push(move)
                self.white.append(pair(key, board))
                iter += 1
        else:
            for move in game.mainline_moves():
                if iter % 2 != 1:
                    board.push(move)
                    iter += 1
                    continue
                key = board
                board.push(move)
                self.white.append(pair(key, board))
                iter += 1

    def createPickle():
        tree = PalmTree(os.path.join(os.getcwd(), "games"))
        out = open(os.path.join(os.getcwd(), "pairWiseData.pt"), 'wb')
        pickle.dump(tree, out)
        out.close()
        print('done')

    def dePickle():
        pick = open(os.path.join(sys.path[0], "PalmTree"), 'rb')
        tree = pickle.load(pick)
        return tree


class PalmTree:
    def __init__(self):
        self.model = None


    def learn(self, pool):
        for gameKey in pool.white:
            for game in pool.white:
                board = chess.Board()
                i = 0
                #We're trying to learn from white's victories


            for game in pool.black:
                i = 0
                #We're trying to learn from black's victories
                for move in game.mainline_moves():
                    board.push(move);
                    rank = self.rank(board)
                    board.pop();
    def pickOpening(self):
        total = 0
        for key in self.white:
            total += len(self.white[key])
        rand = random.randint(0, total)
        total = 0
        for key in self.white:
            total += len(self.white[key])
            if rand < total:
                return key.split(',')[0]

    def makeMove(self, board):
        print('')



def play(tree):
    board = chess.Board()

    whiteOrBlack = random.randint(0, 1)
    if whiteOrBlack == 1:
        print("Tree is white")
        tree.makeMove(board)
    while(not board.is_game_over()):
        print(board)
        playerMove = ""
        while 1 == 1:
            playerMove = input('make your move: ')
            try:
                board.push(board.parse_san(playerMove))
                tree.moves.append(playerMove)
                break
            except:
                continue
        tree.makeMove(board)



if __name__ == '__main__':
    pickle = dePicle(os.path.abspath(os.getcwd()) + '/TestGames')
