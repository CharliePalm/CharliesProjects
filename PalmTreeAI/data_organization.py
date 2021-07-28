import os

import pickle
import chess
import chess.pgn
import chess.svg
import sys
import random
import chess.svg
import numpy as np
import hashlib
import copy

chess_dict_white_to_move = {
    'p' : [1,0,0,0,0,0,0,0,0,0,0,0,0,0],
    'P' : [0,0,0,0,0,0,1,0,0,0,0,0,0,0],
    'n' : [0,1,0,0,0,0,0,0,0,0,0,0,0,0],
    'N' : [0,0,0,0,0,0,0,1,0,0,0,0,0,0],
    'b' : [0,0,1,0,0,0,0,0,0,0,0,0,0,0],
    'B' : [0,0,0,0,0,0,0,0,1,0,0,0,0,0],
    'r' : [0,0,0,1,0,0,0,0,0,0,0,0,0,0],
    'R' : [0,0,0,0,0,0,0,0,0,1,0,0,0,0],
    'q' : [0,0,0,0,1,0,0,0,0,0,0,0,0,0],
    'Q' : [0,0,0,0,0,0,0,0,0,0,1,0,0,0],
    'k' : [0,0,0,0,0,1,0,0,0,0,0,0,0,0],
    'K' : [0,0,0,0,0,0,0,0,0,0,0,1,0,0],
    '.' : [0,0,0,0,0,0,0,0,0,0,0,0,1,0],
}

chess_dict_black_to_move = {
    'p' : [1,0,0,0,0,0,0,0,0,0,0,0,0,1],
    'P' : [0,0,0,0,0,0,1,0,0,0,0,0,0,1],
    'n' : [0,1,0,0,0,0,0,0,0,0,0,0,0,1],
    'N' : [0,0,0,0,0,0,0,1,0,0,0,0,0,1],
    'b' : [0,0,1,0,0,0,0,0,0,0,0,0,0,1],
    'B' : [0,0,0,0,0,0,0,0,1,0,0,0,0,1],
    'r' : [0,0,0,1,0,0,0,0,0,0,0,0,0,1],
    'R' : [0,0,0,0,0,0,0,0,0,1,0,0,0,1],
    'q' : [0,0,0,0,1,0,0,0,0,0,0,0,0,1],
    'Q' : [0,0,0,0,0,0,0,0,0,0,1,0,0,1],
    'k' : [0,0,0,0,0,1,0,0,0,0,0,0,0,1],
    'K' : [0,0,0,0,0,0,0,0,0,0,0,1,0,1],
    '.' : [0,0,0,0,0,0,0,0,0,0,0,0,1,1],
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
    def __init__(self, path, obj=False):
        self.path = path
        self.input = []
        if obj:
            self.output = []
        else:
            self.out1 = []
            self.out2 = []
        self.opening_tree = {}
        self.gather_data(obj)
        #self.input = np.asarray(self.input)
        #self.out1 = np.asarray(self.out1)
        #self.out2 = np.asarray(self.out2)


    def createPickle(name, obj):
        out = open(os.path.join(os.getcwd(), name), 'wb')
        pickle.dump(obj, out)
        out.close()
        return obj

    def dePickle(name):
        pick = open(os.path.join(os.getcwd(), name), 'rb')
        tree = pickle.load(pick)
        return tree


    def gather_data(self, obj):
        for file in os.listdir(self.path):
            print("reading " + file)
            if (file.endswith('pgn')):
                pgn = open(os.path.join(self.path, file))
                game = chess.pgn.read_game(pgn)
                while game is not None:
                    i = 0
                    result = game.headers['Result'].strip()
                    if result == '1-0':
                        self.get_game_data(game, 1, obj)
                    elif result == '0-1':
                        self.get_game_data(game, 0, obj)
                    else:
                        self.get_game_data(game, 1, obj)
                        self.get_game_data(game, 0, obj)
                    try:
                        game = chess.pgn.read_game(pgn)
                    except:
                        game = chess.pgn.read_game(pgn)


    def get_game_data(self, game, whiteOrBlack, obj):
        outer_iter = 0
        board = chess.Board()
        open = []
        if whiteOrBlack:
            for move in game.mainline_moves():
                if outer_iter % 2 != 0:
                    outer_iter = outer_iter + 1
                    board.push(move)
                    continue

                if obj:
                    self.input.append(copy.deepcopy(board))
                    self.output.append(move.uci())
                    board.push(move)
                    continue

                map = board.piece_map()
                inputBoard = []
                iter = 0
                for i in range(1, 9):
                    row = []
                    for j in range(1, 9):

                        if iter not in map:
                            row.append(chess_dict_white_to_move['.'])
                        else:
                            row.append(chess_dict_white_to_move[map[iter].symbol()])
                        iter += 1
                    inputBoard.append(row)

                self.input.append(np.asarray(inputBoard))

                output = self.get_output(chess.Move.uci(move))

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
                if obj:
                    self.input.append(copy.deepcopy(board))
                    self.output.append(move.uci())
                    board.push(move)
                    continue
                map = board.piece_map()
                inputBoard = []
                for i in range(1, 9):
                    row = []
                    for j in range(1, 9):
                        if i + j not in map:
                            row.append(chess_dict_black_to_move['.'])
                        else:
                            row.append(chess_dict_black_to_move[map[i + j].symbol()])
                    inputBoard.append(row)

                self.input.append(np.asarray(inputBoard))

                output = self.get_output(chess.Move.uci(move))

                self.out1.append(output[0])
                self.out2.append(output[1])
                board.push(move)
                outer_iter += 1
        self.add_line(open)

    # this function works to convert a move to a column "probability" vector
    def get_output(self, move):
        arr = [[], []]
        arr[0].append(column_dict[move[0]])
        arr[0].append(row_dict[move[1]])
        arr[1].append(column_dict[move[2]])
        arr[1].append(row_dict[move[3]])
        return arr

    # adds an opening line to the opening tree
    def add_line(self, open):
        node = self.opening_tree
        i = 0
        while i < len(open):
            if open[i] not in node:
                node[open[i]] = {}
                node = node[open[i]]
            else:
                node = node[open[i]]
            i += 1




if __name__ == '__main__':
    a = 2
    while a != 1 and a != 0:
        a = input('object data (1) or one hot data (0)?\n')
        try:
            a = int(a)
        except:
            continue
    if a:
        data = data_organization(os.getcwd() + '/Games', True)
        #test_data = data_organization(os.getcwd() + '/TestGames', True)
    else:
        data = data_organization(os.getcwd() + '/Games')
        test_data = data_organization(os.getcwd() + '/TestGames', True)
    print('pickling data')
    wd = os.getcwd()
    if a:
        data_organization.createPickle(wd + '/data/obj_data.ptd', data)
        #data_organization.createPickle(wd + '/data/obj_test_data.ptd', test_data)
    else:
        data_organization.createPickle(wd + '/data/data.ptd', data)
        data_organization.createPickle(wd + '/data/test_data.ptd', test_data)
