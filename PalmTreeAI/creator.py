import pickle
import chess
import chess.pgn
import chess.svg
import os
import sys
import random
import chess.svg
import numpy as np
import tensorflow as tf
import keras
import Layers
from keras.models import Sequential
from keras.layers import Dense


sys.setrecursionlimit(0x100000)

class dataPool:
    def __init__(self, path):
        self.path = path
        self.data = []
        self.openings = {}
        self.defenses = {}
        self.outputs = []
        self.gatherData()
        self.data = np.asarray(self.data)
        self.output = np.asarray(self.outputs)

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
        opening = None
        defense = None
        if whiteOrBlack:
            for move in game.mainline_moves():
                if iter % 2 != 0:
                    if iter < 4:
                        self.openings[opening].append(move)
                    board.push(move)
                    iter += 1
                    continue
                if iter < 5:
                    if (iter == 0):
                        opening = move
                        self.openings[opening] = []
                    if (iter == 2 or iter == 4):
                        self.openings[opening].append(move)
                    iter += 1
                    board.push(move)
                    continue

                self.data.append(board)
                board.push(move)
                self.outputs.append(move)
                iter += 1
        else:
            for move in game.mainline_moves():
                if iter == 0:
                    defense = move
                    self.defenses[defense] = []
                    iter += 1
                    board.push(move)
                    continue
                if iter % 2 != 1:
                    if (iter == 2 or iter == 4):
                        self.defenses[defense].append(move)
                    board.push(move)
                    iter += 1
                    continue
                if iter == 1 or iter == 3 or iter == 5:
                    self.defenses[defense].append(move)
                    iter += 1
                    board.push(move)
                    continue

                self.data.append(board)
                board.push(move)
                self.outputs.append(move)
                iter += 1

    def createPickle(path, name):
        tree = dataPool(path)
        out = open(os.path.join(os.getcwd(), name), 'wb')
        pickle.dump(tree, out)
        out.close()
        print('done')

    def dePickle(name):
        pick = open(os.path.join(sys.path[0], name), 'rb')
        tree = pickle.load(pick)
        return tree


class PalmTree:
    def __init__(self, pickle):
        self.openings = pickle.openings
        self.defenses = pickle.defenses
        self.a = 1
        self.b = 1
        self.c = 1
        self.d = 1
        self.e = 1
        Layers.model(self, pickle.data, pickle.outputs)


    def makeMove(self, board):
        move = self.model.predict([board, board.legal_moves])
        board.push(move)
        return board

    def makeMove(self, board):
        move = Layers.choose(self, board)
        return move

def play(tree):
    board = chess.Board()
    whiteOrBlack = random.randint(1, 0)
    if (whiteOrBlack):
        move = tree.makeMove(board)
        board.push(move)
        return board

    userInput = ''
    while (userInput != 'q' or userInput != 'Q'):
        if whiteOrBlack:
            chess.svg.board(board, orientation=chess.Black)
        else:
            chess.svg.board(board, orientation=chess.White)
        while 1:
            userInput = input("\n")
            try:
                board.push(userInput)
                break
            except:
                continue

        board = tree.makeMove(board)

def model(data, test_data):
    tree = PalmTree(pool)

if __name__ == '__main__':
    data = dataPool.createPickle(os.getcwd() + '/Games', 'data')
    test_data = dataPool.createPickle(os.getcwd() + '/TestGames', "test_data")
