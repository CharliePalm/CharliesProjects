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
import tensorflow as tf
from creator import PalmTree
from keras import backend as k
from keras.layers.core import Activation, Dense, Flatten


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

class a_star_model(PalmTree, keras.Model):
    def __init__(self, depth):
        self.rate = self.model(1)
        self.depth = depth

    def build_rating_model():
        print("building input")
        input = x = keras.engine.topology.Input((14, 8, 8))

        x = keras.layers.DepthwiseConv2D(padding='same', filters=24, kernel_size=2, use_bias=False, data_format="channels_first")(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = keras.layers.convolutional.Conv2D(padding='same', filters=48, kernel_size=3, data_format="channels_first")(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        a = x = keras.layers.convolutional.Conv2D(padding='same', filters=64, use_bias=False, kernel_size=4, data_format="channels_first")(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = keras.layers.DepthwiseConv2D(padding='same', filters=64, use_bias=False, kernel_size=4)(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = keras.layers.merge.Add()[a, x]

        x = keras.layers.convolutional.Conv2D(padding='same', filters=48, kernel_size=3, data_format="channels_first")(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)

        x = keras.layers.DepthwiseConv2D(padding='same', filters=24, kernel_size=2, use_bias=False)(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("tanh")(x)

        x = Flatten()(out)
        x = Dense(256)(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(64)(x)
        x = Activation("tanh")(x)
        x = Dense(36)(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(12)(x)
        x = Activation("sigmoid")(x)
        x = Dense(4)(x)
        x = keras.layers.BatchNormalization(axis=1)(x)
        x = Activation("relu")(x)
        x = Dense(1)(x)
        x = Activation("sigmoid")(x)

        return Model(input, x)

def predict(input, ):
    

def a_star_search(self, board, depth, max_depth, train):
    if board.is_checkmate() and depth % 2 == 1:
        return 0
    if board.is_checkmate() and depth % 2 == 0:
        return 1 / depth

    if depth == max_depth:
        return 0
    moves = {}
    for move in board.legal_moves:
        board.push(move)
        input = self.create_board(board, board.turn)
        val = self.predict(input, training=train)[0][0]
        moves[move.uci()] = val
        avg += val


    for m in moves:

        values[v] += self.a_star_search(boards[values[v]], depth + 1, max_depth)

    if depth == 0 and not train:
        return boards[max(values)].pop()
    if depth == 0 and train:
        return values, boards
    return max(values)



def create_board(self, board, white):
    return super().create_board(board, white)

a = a_star_model(5)
