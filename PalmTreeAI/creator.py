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
from keras.models import Sequential
from keras.layers import Dense


sys.setrecursionlimit(0x100000)

class dataPool:
    def __init__(self, path):
        self.path = path
        self.data = []
        self.openings = []
        self.output = []
        self.gatherData()
        self.data = np.asarray(self.data, dtype=object)
        self.output = np.asarray(self.output, dtype=object)

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

                self.data.append([board, board.legal_moves])
                self.output.append(move)
                board.push(move)
                iter += 1
        else:
            for move in game.mainline_moves():
                if iter % 2 != 1:
                    board.push(move)
                    iter += 1
                    continue
                key = board
                board.push(move)
                self.data.append([board, board.legal_moves])
                self.output.append(move)
                iter += 1

    def createPickle(path):
        tree = dataPool(path)
        out = open(os.path.join(os.getcwd(), "test_data.pt"), 'wb')
        pickle.dump(tree, out)
        out.close()
        print('done')

    def dePickle(name):
        pick = open(os.path.join(sys.path[0], name), 'rb')
        tree = pickle.load(pick)
        return tree


class PalmTree:
    def __init__(model):
        self.model = model


    def makeMove(self, board):
        move = self.model.predict([board, board.legal_moves])
        board.push(move)
        return board

def play(tree):
    board = chess.Board()
    whiteOrBlack = random.randint(1, 0)
    if (whiteOrBlack):
        tree.makeMove(board)

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
    model = Sequential()
    print("starting fit")
    model.add(keras.Input(shape=(2,)))
    model.add(Dense(units=32, activation='softmax'))
    model.add(Dense(units=16, activation='relu'))
    model.add(Dense(units=1, activation='sigmoid'))
    model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

    model.fit(data.data, data.output, epochs=1)

    metrics = model.evaluate(test_data.data, test_data.output)
    print(metrics)
    play(tree)

if __name__ == '__main__':
    data = dataPool.dePickle('data.pt')
    test_data = dataPool.dePickle('test_data.pt')
    model(data, test_data)
