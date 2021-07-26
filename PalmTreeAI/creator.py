import os

import plaidml.keras
plaidml.keras.install_backend()
os.environ["KERAS_BACKEND"] = "plaidml.keras.backend"

from data_organization import data_organization
from lichess_interact import Lichess_Interact
import datetime
import pickle
import chess
#import chess.pgn
#import chess.svg
import sys
import random
#import chess.svg
import numpy as np
import copy
import matplotlib.pyplot as plt
import keras
from keras import backend as k
from keras.engine.topology import Input
from keras.engine.training import Model
from keras.layers.convolutional import Conv2D
from keras.layers.core import Activation, Dense, Flatten
from keras.layers import MaxPooling2D
from keras.layers.merge import Add
from keras.layers.normalization import BatchNormalization
from keras.regularizers import l2
from keras.callbacks import TensorBoard
import keras.applications as kapp


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
sys.setrecursionlimit(0x100000)


class PalmTree:
    def __init__(self, layers):
        self.model = self.model(layers)
        print(self.model.summary())
        self.lichess = Lichess_Interact()



    def simple_model(self, layers):
        print("building simple input")
        input = x = Input(shape=(12,8,8))
        x = BatchNormalization(name="in_2", axis=1)(x)
        x = Conv2D(padding='same', filters=64, kernel_size=4, use_biase=False, data_format="channels_first", name="in_1")
        x = Activation("relu", name="in_3")(x)
        for i in range(layers):
            self.build_residuals(x, i)
        return Model(input, [out1, out2], name="palmtree")

    #modeled after the supervised learning approach in the chess alpha zero model
    def model(self, layers):
        print("building input")
        input = x = Input((14, 8, 8))

        x = Conv2D(padding='same', filters=24, kernel_size=2, use_bias=False, data_format="channels_first", name="Conv2D_in_1")(x)
        x = BatchNormalization(axis=1, name="input_batchnorm")(x)
        x = Activation("relu")(x)
        x = Conv2D(padding='same', filters=48, kernel_size=3, data_format="channels_first", name="Conv2D_in_2")(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Conv2D(padding='same', filters=64, use_bias=False, kernel_size=4, data_format="channels_first", name="Conv2D1_in_3")(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Conv2D(padding='same', filters=128, use_bias=False, kernel_size=5, data_format="channels_first", name="Conv2D1_in_4")(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Conv2D(padding='same', filters=256, use_bias=False, kernel_size=6, data_format="channels_first", name="Conv2D1_in_5")(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        print("building residuals")

        for i in range(layers):
            x = self.build_residuals(x, i)

        out = x

        x = Conv2D(padding='same', filters=128, kernel_size=3, data_format="channels_first")(out)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(padding='same', filters=64, kernel_size=3, data_format="channels_first")(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(filters=32, kernel_size=3, use_bias=False, data_format="channels_first")(x)
        #x = MaxPooling2D(pool_size=(2,2), padding='valid')(x)

        x = Flatten()(x)
        x = Dense(512)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(256)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        from_column = Dense(8, activation="softmax", name='from_column')(x)



        x = Conv2D(padding='same', filters=128, kernel_size=3, data_format="channels_first")(out)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(padding='same', filters=64, kernel_size=3, data_format="channels_first")(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(filters=32, kernel_size=3, use_bias=False, data_format="channels_first")(x)
        #x = MaxPooling2D(pool_size=(2,2), padding='valid')(x)

        x = Flatten()(x)
        x = Dense(512)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(256)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        from_row = Dense(8, activation="softmax", name='from_row')(x)



        x = Conv2D(padding='same', filters=128, kernel_size=3, data_format="channels_first")(out)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(padding='same', filters=64, kernel_size=3, data_format="channels_first")(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(filters=32, kernel_size=3, use_bias=False, data_format="channels_first")(x)
        #x = MaxPooling2D(pool_size=(2,2), padding='valid')(x)


        x = Flatten()(x)
        x = Dense(512)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(256)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        to_column = Dense(8, activation="softmax", name='to_column')(x)


        x = Conv2D(padding='same', filters=128, kernel_size=3, data_format="channels_first")(out)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(padding='same', filters=64, kernel_size=3, data_format="channels_first")(x)
        x = Activation("relu")(x)
        x = BatchNormalization(axis=1)(x)
        x = Conv2D(filters=32, kernel_size=3, use_bias=False, data_format="channels_first")(x)
        #x = MaxPooling2D(pool_size=(2,2), padding='valid')(x)

        x = Flatten()(x)
        x = Dense(512)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(256)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = Activation("relu")(x)
        to_row = Dense(8, activation="softmax", name='to_row')(x)

        print("Done building model")
        return Model(input, [from_column, from_row, to_column, to_row], name="palmtree")



    def build_residuals(self, x, i):
        print("building residual layer ", i)
        input = x
        x = Conv2D(padding='same', filters=256, use_bias=False, kernel_size=6, data_format="channels_first", name="Residual_Conv2D1_" + str(i))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Conv2D(padding='same', filters=256, use_bias=False, kernel_size=6, data_format="channels_first", name="Residual_Conv2D2_"+ str(i))(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Add(name="Residual_Add_" + str(i))([input, x])
        return x

    def create_board(self, board, whiteOrBlack):
        map = board.piece_map()
        inputBoard = []
        iter = 0
        for i in range(1, 9):
            row = []
            for j in range(1, 9):
                if iter not in map:
                    if whiteOrBlack:
                        row.append(chess_dict_white_to_move['.'])
                    else:
                        row.append(chess_dict_black_to_move['.'])
                else:
                    if whiteOrBlack:
                        row.append(chess_dict_white_to_move[map[iter].symbol()])
                    else:
                        row.append(chess_dict_black_to_move[map[iter].symbol()])
                iter += 1
            inputBoard.append(row)
        return inputBoard



    def make_move(self, board, whiteOrBlack):
        input_board = self.create_board(board, whiteOrBlack)
        input_board = np.transpose(input_board)
        move = self.model.predict_on_batch([[input_board]])
        move_copy = copy.deepcopy(move)
        for i in range(len(move_copy)):
            move_copy[i] = np.sort(move_copy[i])

        possible_moves = {}
        for i in range(8):
            z1 = np.zeros(shape=(8))
            z1[i] = 1
            s = move[0][0][i]
            for j in range(8):
                z2 = np.zeros(shape=(8))
                z2[j] = 1
                s += move[1][0][j]
                for k in range(8):
                    z3 = np.zeros(shape=(8))
                    z3[k] = 1
                    s += move[2][0][k]
                    for l in range(8):
                        z4 = np.zeros(shape=(8))
                        z4[l] = 1
                        s += move[3][0][l]
                        possible_moves[float(s)] = copy.deepcopy(np.array([z1, z2, z3, z4]))
                        s -= move[3][0][l]
                    s -= move[2][0][k]
                s -= move[1][0][j]
        sums = list(possible_moves.keys())
        sums.sort()
        sums.reverse()
        sums = sums[0:50]
        sums = np.asarray(sums)
        probs = sums / sum(sums)
        probs = list(probs)
        sums = list(sums)
        for i in range(50):
            c = np.random.choice(a=sums, p=probs)
            move = self.convert_to_valid_move(possible_moves[c])
            if self.check_legal(move, board):
                return move
            i = int(np.where(sums == c)[0])
            a = probs[i]
            del sums[i], probs[i]

            probs += (a / (len(probs)))
            probs = list(probs)
        move = np.random.choice(list(board.legal_moves)).uci()
        return move

    def check_legal(self, move, board):
        for legal in board.legal_moves:
            if move.lower() == legal.uci().lower():
                return True
        return False

    def convert_to_valid_move(self, one_hot):
        move = ""
        for i in column_dict:
            if np.allclose(one_hot[0], column_dict[i]):
                move+=i
                break

        for i in row_dict:
            if np.allclose(one_hot[1], row_dict[i]):
                move+=i
                break

        for i in column_dict:
            if np.allclose(one_hot[2], column_dict[i]):
                move+=i
                break

        for i in row_dict:
            if np.allclose(one_hot[3], row_dict[i]):
                move+=i
                break

        return move



def play(tree):
    board = chess.Board()
    whiteOrBlack = random.choice([0, 1])
    if (whiteOrBlack):
        print('Albert plays white, you play black')
        move = tree.makeMove(board, whiteOrBlack)
        board.push(move)

    userInput = ''
    while (userInput != 'q' or userInput != 'Q'):
        print(board)
        """
        if whiteOrBlack:
            chess.svg.board(board, orientation=chess.BLACK)
        else:
            chess.svg.board(board, orientation=chess.WHITE)
        """
        while 1:
            userInput = input("\n")
            try:
                move = chess.Move.from_uci(userInput)
                if move in board.legal_moves:
                    board.push(move)
                    break
                else:
                    print('invalid move')
                    continue
            except:
                continue
        print(board)
        move = tree.makeMove(board)
        print('I think I will play', move)
        board.push(move)




if __name__ == '__main__':
    print("Currently it is " + str(datetime.datetime.time(datetime.datetime.now())))

    test_data = data_organization.dePickle('data/test_data.ptd')
    test_data.out1 = np.asarray(test_data.out1)
    test_data.out2 = np.asarray(test_data.out2)



    tree = PalmTree(1)
    opt = keras.optimizers.Adam(lr=.000001)
    #metrics = [tf.metrics.CategoricalAccuracy(name="categorical_accuracy")]

    tree.model.compile(optimizer=opt, metrics=['categorical_accuracy'], loss='categorical_crossentropy')

    print("done compiling, depickling data")

    data = data_organization.dePickle('data/data.ptd')
    data.out1 = np.asarray(data.out1)
    data.out2 = np.asarray(data.out2)

    for i in range(len(data.input)):
        data.input[i] = np.transpose(data.input[i])
    print('done depickling data: fitting')
    h = tree.model.fit(x=np.asarray(data.input[:200000]), y=[data.out1[:,0][:200000], data.out1[:,1][:200000], data.out2[:,0][:200000], data.out2[:,1][:200000]], epochs=10, verbose=1, batch_size=256)

    print("Pickling tree")
    data_organization.createPickle(os.getcwd() + '/models/PalmTree1.1', tree)
    from_row = h.history['from_column_categorical_accuracy']
    from_col = h.history['from_row_categorical_accuracy']
    to_row = h.history['to_row_categorical_accuracy']
    to_col = h.history['to_column_categorical_accuracy']
    epoch_count = range(1, len(to_row) + 1)


    plt.plot(epoch_count, to_col)
    plt.plot(epoch_count, from_row)
    plt.plot(epoch_count, to_row)
    plt.plot(epoch_count, from_col)
    plt.show()
    #tree.model.save('./PalmTreeAI/models/test_model')

    #tree = data_organization.dePickle('models/Albert_model_5')
    #print('done loading tree')
    #print("evaluating tree")
    #score = tree.model.evaluate(x=np.asarray(test_data.input), y=[test_data.out1[:,0], test_data.out1[:,1], test_data.out2[:,0], test_data.out2[:,1]], verbose=1)
    #play(tree)
    '''
    i = 0
    for input in test_data.input:
        i += 1
        print('output')
        print(test_data.out1[i][0])
        print(test_data.out1[i][1])
        print(test_data.out2[i][0])
        print(test_data.out2[i][1])
        pred = tree.model.predict([[input]])
        print('albert predicted:')
        for j in pred:
            print(j)
    '''
