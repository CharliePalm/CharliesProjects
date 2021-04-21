import os
"""
os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"
os.environ["RUNFILES_DIR"] = "/Library/Frameworks/Python.framework/Versions/3.7/share/plaidml"
os.environ["PLAIDML_NATIVE_PATH"] = "/Library/Frameworks/Python.framework/Versions/3.8/lib/libplaidml.dylib"
"""


import pickle
import chess
import chess.pgn
import chess.svg
import sys
import random
import chess.svg
import numpy as np
import pyopencl as cl
import hashlib
import copy

chess_dict = {
    'p' : [1,0,0,0,0,0,0,0,0,0,0,0,0],
    'P' : [0,0,0,0,0,0,1,0,0,0,0,0,0],
    'n' : [0,1,0,0,0,0,0,0,0,0,0,0,0],
    'N' : [0,0,0,0,0,0,0,1,0,0,0,0,0],
    'b' : [0,0,1,0,0,0,0,0,0,0,0,0,0],
    'B' : [0,0,0,0,0,0,0,0,1,0,0,0,0],
    'r' : [0,0,0,1,0,0,0,0,0,0,0,0,0],
    'R' : [0,0,0,0,0,0,0,0,0,1,0,0,0],
    'q' : [0,0,0,0,1,0,0,0,0,0,0,0,0],
    'Q' : [0,0,0,0,0,0,0,0,0,0,1,0,0],
    'k' : [0,0,0,0,0,1,0,0,0,0,0,0,0],
    'K' : [0,0,0,0,0,0,0,0,0,0,0,1,0],
    '.' : [0,0,0,0,0,0,0,0,0,0,0,0,1],
}
column_dict = {
    'a' : [1,0,0,0,0,0,0,0],
    'b' : [0,1,0,0,0,0,0,0],
    'c' : [0,0,1,0,0,0,0,0],
    'd' : [0,0,0,1,0,0,0,0],
    'e' : [0,0,0,0,1,0,0,0],
    'f' : [0,0,0,0,0,1,0,0],
    'g' : [0,0,0,0,0,0,1,0],
    'h' : [0,0,0,0,0,0,0,1],
}
row_dict = {

    '1' : [1,0,0,0,0,0,0,0],
    '2' : [0,1,0,0,0,0,0,0],
    '3' : [0,0,1,0,0,0,0,0],
    '4' : [0,0,0,1,0,0,0,0],
    '5' : [0,0,0,0,1,0,0,0],
    '6' : [0,0,0,0,0,1,0,0],
    '7' : [0,0,0,0,0,0,1,0],
    '8' : [0,0,0,0,0,0,0,1],
}

class data_organization:
    def __init__(self, path):
        self.path = path
        self.input = []
        self.out1 = []
        self.out2 = []
        self.openings = {}
        self.defenses = {}
        self.gather_data()
        #self.input = np.asarray(self.input)
        #self.out1 = np.asarray(self.out1)
        #self.out2 = np.asarray(self.out2)


    def createPickle(name, obj):
        out = open(os.path.join(os.getcwd(), name), 'wb')
        pickle.dump(obj, out)
        out.close()
        return obj

    def dePickle(name):
        pick = open(os.path.join(sys.path[0], name), 'rb')
        tree = pickle.load(pick)
        return tree


    def gather_data(self):
        for file in os.listdir(self.path):
            print("reading " + file)
            if (file.endswith('pgn')):
                pgn = open(os.path.join(self.path, file))
                game = chess.pgn.read_game(pgn)
                while game is not None:
                    i = 0
                    result = game.headers['Result'].strip()
                    if result == '1-0':
                        self.get_game_data_no_openings(game, 1)
                    elif result == '0-1':
                        self.get_game_data_no_openings(game, 0)
                    else:
                        self.get_game_data_no_openings(game, 1)
                        self.get_game_data_no_openings(game, 0)
                    try:
                        game = chess.pgn.read_game(pgn)
                    except:
                        game = chess.pgn.read_game(pgn)


    def get_game_data_no_openings(self, game, whiteOrBlack):
        outer_iter = 0
        board = chess.Board()
        if whiteOrBlack:

            for move in game.mainline_moves():
                if outer_iter % 2 != 0:
                    outer_iter = outer_iter + 1
                    board.push(move)
                    continue

                #newBoard = copy.deepcopy(board)
                map = board.piece_map()
                inputBoard = []
                iter = 0
                for i in range(1, 9):
                    row = []
                    for j in range(1, 9):

                        if iter not in map:
                            row.append(chess_dict['.'])
                        else:
                            row.append(chess_dict[map[iter].symbol()])
                        iter += 1
                    inputBoard.append(row)

                self.input.append(np.asarray(inputBoard))

                output = self.getOutput(chess.Move.uci(move))

                self.out1.append(output[0])
                self.out2.append(output[1])
                board.push(move)
                outer_iter += 1

        else:
            for move in game.mainline_moves():
                if outer_iter % 2 != 1:
                    outer_iter += 1
                    board.push(move)
                    continue

                #newBoard = copy.deepcopy(board)
                map = board.piece_map()
                inputBoard = []
                iter = 0
                for i in range(1, 9):
                    row = []
                    for j in range(1, 9):

                        if iter not in map:
                            row.append(chess_dict['.'])
                        else:
                            row.append(chess_dict[map[iter].symbol()])
                        iter += 1
                    inputBoard.append(row)


                self.input.append(np.asarray(np.flip(inputBoard)))
                output = self.getOutput(chess.Move.uci(move))
                if np.allclose(np.zeros(shape=(8,8,12)), inputBoard):
                    print('zero board')
                    print(map)
                self.out1.append(output[0])
                self.out2.append(output[1])
                board.push(move)
                outer_iter += 1



    #this function works to convert a move to a column probability vector
    def getOutput(self, move):
        arr = [[], []]
        arr[0].append(column_dict[move[0]])
        arr[0].append(row_dict[move[1]])
        arr[1].append(column_dict[move[2]])
        arr[1].append(row_dict[move[3]])
        return arr



if __name__ == '__main__':

    data = data_organization(os.getcwd() + '/Games')
    data = data_organization.createPickle(os.getcwd() + '/data/data', data)



    test_data = data_organization(os.getcwd() + '/TestGames')
    test_data = data_organization.createPickle(os.getcwd() + '/data/test_data', test_data)
