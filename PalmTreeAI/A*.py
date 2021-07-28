import os
import tensorflow as tf

def get_mkl_enabled_flag():

    mkl_enabled = False
    major_version = int(tf.__version__.split(".")[0])
    minor_version = int(tf.__version__.split(".")[1])
    if major_version >= 2:
        if minor_version < 5:
            from tensorflow.python import _pywrap_util_port
        else:
            from tensorflow.python.util import _pywrap_util_port
            onednn_enabled = int(os.environ.get('TF_ENABLE_ONEDNN_OPTS', '0'))
        mkl_enabled = _pywrap_util_port.IsMklEnabled() or (onednn_enabled == 1)
    else:
        mkl_enabled = tf.pywrap_tensorflow.IsMklEnabled()
    return mkl_enabled

print ("We are using Tensorflow version", tf.__version__)
print("MKL enabled :", get_mkl_enabled_flag())
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

class a_star_model(tf.keras.Model):
    def __init__(self, depth):
        super(a_star_model, self).__init__()
        self.rating_model = self.build_rating_model()
        self.depth = depth

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
        x = Dense(1024)(x)
        x = Activation("relu")(x)
        x = Dense(512)(x)
        x = Activation("relu")(x)
        x = Dense(128)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = Activation("relu")(x)
        x = Dense(32)(x)
        x = Activation("relu")(x)
        x = Dense(1)(x)

        return tf.keras.Model(input, x)

    def predict(self, x, y=None):
        x = np.transpose(x)
        x = np.asarray([x], dtype='float32')
        if not y:
            return self.rating_model(x)[0]
        else:
            return self.rating_model(x,training=True)[0]

    def best_move(self, board, training):
        moves = self.a_star_search(board, 0, training)
        return moves[max(moves, key=moves.get)]

    def train_step(self, x, y, optimizer, loss_fn, metrics):
        with tf.GradientTape() as tape:
            tensors, best_move = self.a_star_search(x, y, 0, training=True)
            y_pred = tensors[best_move]

            if y not in tensors:
                tensors[y] = np.asarray([0.0], dtype='float32')

            print(y_pred, tensors[best_move])
            print(y, tensors[y])
            loss_value = loss_fn(y_pred, tensors[y])

        grads = tape.gradient(loss_value, self.rating_model.trainable_weights)
        optimizer.apply_gradients(zip(grads, self.rating_model.trainable_weights))
        metrics.update_state(tensors[y], y_pred)
        return loss_value

    def train(self, x, y, epochs, verbose, batch_size):

        opt = tf.keras.optimizers.Adam(lr=.001)
        metrics = tf.keras.metrics.Accuracy()
        loss = tf.keras.losses.MeanSquaredError()

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
                print('loss: ', float(batch_loss/l))

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
        for move in board.legal_moves:
            board.push(move)
            input = self.create_board(board, board.turn)
            board.pop()
            tensor = self.predict(input, y)
            val = tensor.numpy()[0]
            moves.setdefault(val, move.uci())
            tensors[move.uci()] = tensor

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


print('making object')
a = a_star_model(3)



opt = tf.keras.optimizers.Adam(learning_rate=.001)
metrics = tf.keras.metrics.MeanAbsolutePercentageError()
loss = tf.keras.losses.MeanSquaredError()
a.rating_model.compile(optimizer=opt, metrics=metrics, loss=loss)
a.rating_model.summary()

a.compile(optimizer=opt, metrics=metrics, loss=loss)
print('beginning to depickle data')
data = data_organization.dePickle('data/obj_data.ptd')

print('training')

h = a.train(x=data.input[:300], y=data.output[:300], epochs=5, verbose=1, batch_size=20)

data_organization.createPickle(os.getcwd() + '/models/a_star_v1', a.rating_model)
