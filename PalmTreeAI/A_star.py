import os
import tensorflow as tf

from data_organization import data_organization
from lichess_interact import Lichess_Interact
import pickle
import chess
#import chess.pgn
#import chess.svg
import sys
import random
#import chess.svg
import numpy as np
import copy
from sortedcontainers import SortedDict
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Flatten, Add, Dense, Conv2D, BatchNormalization, Activation, DepthwiseConv2D
from tensorflow.keras import Input
import time
import weakref


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

class a_star_model():
    def __init__(self, depth):
        self.rating_model = self.build_rating_model()
        self.depth = depth
        self.lichess = None
        self.avg = 5
        self.iter = 0
        self.predict_val = 0

    def build_rating_model(self):

        input = x = Input((14, 8, 8))

        x = Conv2D(padding='same', filters=24, kernel_size=2)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = Conv2D(padding='same', filters=48, kernel_size=3)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = Conv2D(padding='same', filters=64, kernel_size=4)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = Conv2D(padding='same', filters=48, kernel_size=3)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("exponential")(x)

        x = Conv2D(padding='same', filters=24, kernel_size=2)(x)
        x = BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = Flatten()(x)
        x = Dense(512)(x)
        x = Activation("relu")(x)
        x = Dense(128)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = Activation("relu")(x)
        x = Dense(32)(x)
        x = Activation("relu")(x)
        x = Dense(1)(x)
        x = Activation("sigmoid")(x)

        return tf.keras.Model(input, x)

    def predict(self, x, y=None):
        self.predict_val += 1
        x = np.transpose(x)
        x = np.asarray([x], dtype='float32')
        if not y:
            return self.rating_model(x)[0]
        else:
            return self.rating_model(x,training=True)[0]

    def make_move(self, x):
        return self.a_star_search(self, x, None, self.depth, False)

    def train_step(self, x, y, optimizer, loss_fn, metrics):
        moves = SortedDict()
        tensors = {}
        local_avg = 0
        iter = 0
        with tf.GradientTape() as tape:
            for move in x.legal_moves:
                iter += 1
                x.push(move)
                input = self.create_board(x, x.turn)
                x.pop()
                tensor = self.predict(input, y)
                val = tensor.numpy()[0]
                if val >= self.avg + (1 + self.avg) / 4:
                    val += self.a_star_search(x, y, 1, True)
                tensors[move.uci()] = tensor, val
                moves.setdefault(val, move.uci())
                if y == move.uci():
                    correct_move_val = val
                local_avg *= iter - 1
                local_avg += val
                local_avg /= iter

            y_pred = moves.peekitem()[0]
            pred_move = moves.peekitem()[1]
            pred_vals = moves.keys()
            true_arr = []
            pred_arr = []
            search = True
            i = 0
            for p in moves.__reversed__():
                pred_arr.append(tensors[moves[p]][0])
                if moves[p] != y and search:
                    to_add = tf.convert_to_tensor(np.array([p - abs((p - y_pred) / (p + self.avg))], dtype='float32'))
                    true_arr.append(to_add)
                elif search:
                    to_add = tf.convert_to_tensor(np.array([y_pred + abs(self.avg / y_pred)], dtype='float32'))
                    true_arr.append(to_add)
                else:
                    to_add = tf.convert_to_tensor(np.array([p], dtype='float32'))
                    true_arr.append(to_add)
                tape.watch(to_add)
                i += 1

            self.avg = (self.avg * iter + abs(local_avg)) / (iter + 1)
            self.iter += 1
            loss_value = loss_fn(true_arr, pred_arr)
            grads = tape.gradient(loss_value, self.rating_model.trainable_weights)
        print('loss: ', loss_value)
        print('avg: ', self.avg)
        print('y_true: ', y, correct_move_val)
        print('y_pred: ', moves[y_pred], y_pred)
        print('model evaluated ' + str(self.predict_val) + ' positions')
        optimizer.apply_gradients(zip(grads, self.rating_model.trainable_weights))
        return loss_value

    def train(self, x, y, epochs, verbose, batch_size):

        opt = tf.keras.optimizers.Adam(lr=.00001)
        metrics = tf.keras.metrics.Accuracy()
        loss = tf.keras.losses.MeanSquaredError()
        a.rating_model.compile(optimizer=opt, metrics=metrics, loss=loss)

        for i in range(epochs):
            print('epoch ' + str(i))
            l = 0
            batch_loss = 0
            u = batch_size
            while u < len(x):
                for i in range(l, u):
                    batch_loss += self.train_step(x[i], y[i], opt, loss, metrics)
                u += batch_size
                l += batch_size
                print('\n\nloss: ', float(batch_loss/l))
                print('\n')

    def a_star_search(self, board, y, depth, training):
        if board.is_checkmate() and depth % 2 == 1:
            return 0
        if board.is_checkmate() and depth % 2 == 0:
            return 1 / depth
        if board.is_stalemate():
            return 0

        if depth == self.depth:
            return 0

        moves = SortedDict()
        tensors = {}
        avg = 0
        iter = 0
        for move in board.legal_moves:
            iter += 1
            board.push(move)
            input = self.create_board(board, board.turn)
            board.pop()
            tensor = self.predict(input, y)
            val = tensor.numpy()[0]
            if val >= self.avg + (1 + self.avg) / 4:
                moves.setdefault(val, move.uci())
                tensors[move.uci()] = tensor
            avg *= iter - 1
            avg += val
            avg /= iter

        maxim = 0
        best_move = None
        iter = 0
        keys = moves.keys()
        best_moves = {}
        to_ret_tensors = {}
        #find the highest rated third of moves and find their children
        for i in range(3 * int(len(keys) / 4), len(keys)):
            board.push(chess.Move.from_uci(moves[keys[i]]))
            best_moves[moves[keys[i]]] = self.a_star_search(board, y, depth + 1, training) + keys[i]
            to_ret_tensors[moves[keys[i]]] = tensors[moves[keys[i]]]

            if best_moves[moves[keys[i]]] >= maxim or not best_move:
                maxim = best_moves[moves[keys[i]]]
                best_move = moves[keys[i]]
            board.pop()


        if depth == 0:
            return to_ret_tensors, best_move
        if not best_move:
            return 0
        return best_moves[best_move]

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

class testData:
    def __init__(self):
        b1 = chess.Board()
        b2 = chess.Board()
        b2.push(chess.Move.from_uci('e2e4'))
        self.input = [b1, b2]
        self.output = ['e2e4', 'e7e5']


if __name__ == '__main__':
    print('making object')
    a = a_star_model(4)


    test = input('is this a test? y/n\n')
    if test == 'y':
        test = True
    else:
        test = False

    if not test:
        print('beginning to depickle data')
        data = data_organization.dePickle('data/obj_data.ptd')
    else:
        data = testData()

    print('training')
    h = a.train(x=data.input[:500], y=data.output[:500], epochs=5, verbose=1, batch_size=1)
    a.rating_model.save(os.getcwd() + '/models/a_star_v1')
    del a.rating_model

    data_organization.createPickle(os.getcwd() + '/models/a_star_v1_obj', a)
