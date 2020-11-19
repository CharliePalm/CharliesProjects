import pickle
import chess
import chess.pgn
import chess.svg
import os
import sys
import random
import chess.svg
import numpy as np

outputs = {}
predicts = {}
def model(model, inputs, out):
    for board in inputs:
        inputLayer(model, board, out)

def predict(model, board):
    for move in moves:
        predicts[move] = {}
        board.push(move)
        layer2(board, move)
        layer3(board, move)
        layer4(board, move)
        layer5(board, move)
        board.pop()
    move = decide(model)
    predicts = {}
    return move
"""
This model operates in a bit of an unconventional manner:
the input layer, instead of passing through the neural network with the output of
the previous layer to determine the output, instead weighs the output of each layer
as a separate factor in determining which of the moves in board.legal_moves is the
'best of both worlds'
"""
def inputLayer(model, board, out):
    moves = board.legal_moves
    i = 0
    for move in moves:
        outputs[move] = {}
        board.push(move)
        layer2(board, move)
        layer3(board, move)
        layer4(board, move)
        layer5(board, move)
        layer6(model, board, move)
        board.pop()
    move = decide(model)
    outputLayer(model, move, out[i])
    i += 1
    outputs = {}

#Layer 2 analyzes the significance of the increase in number of attacks
def layer2(board, move):
    outputs[move[2]] = board.attacks(move.to_square)

#Layer 3 analyzes the significance of the decrease in opponent attacks
def layer3(board, move):
    myMove = board.pop()
    oppMove = board.pop()
    board.push(oppMove)
    opAtk1 = board.attacks(oppMove.to_square)
    board.push(myMove)
    opAtk2 = board.attacks(oppMove.to_square)
    outputs[move[3]] = opAtk1 - opAtk2

#layer 4 checks for checkmate. We know we want checkmate but the machine initially does not!
def layer4(board, move):
    if (board.is_checkmate()):
        outputs[move[4]] = 1
    else:
        outputs[move[4]] = 0

# layer 5 checks for attacks by opponent at move
def layer5(board, move):
    attackers = board.attackers(move.to_square)
    outputs[move[5]] = len(attackers)

# layer 6 is a recursive lookahead for disadvantages
def layer6(model, board, move):
    opMove = predict(model, board)
    


def decide(model):
    bestMove = None
    for move in outputs:
        outputs[move[sum]] = model.a * outputs[move[1]] + model.b * outputs[move[2]] + model.c * outputs[move[3]] + model.d * outputs[move[4]] + model.e * outputs[move[5]]
        if not bestMove or outputs[move[sum]] > outputs[bestMove[sum]]:
            bestMove = move
    return bestMove

def outputLayer(model, m, cm):
    if (move != cm):
        if outputs[m[1]] < outputs[cm[1]]:
            model.a += (outputs[cm[1]] - outputs[m[1]]) ** .5
        else:
            model.a -= (outputs[cm[1]] - outputs[m[1]]) ** .5

        if outputs[m[2]] < outputs[cm[2]]:
            model.b += (outputs[cm[2]] - outputs[m[2]]) ** .5
        else:
            model.b -= (outputs[cm[2]] - outputs[m[2]]) ** .5

        if outputs[m[3]] < outputs[cm[3]]:
            model.c += (outputs[cm[3]] - outputs[m[3]]) ** .5
        else:
            model.c -= (outputs[cm[3]] - outputs[m[3]]) ** .5

        if outputs[m[4]] < outputs[cm[4]]:
            model.d += (outputs[cm[4]] - outputs[m[4]]) ** .5
        else:
            model.d -= (outputs[cm[4]] - outputs[m[4]]) ** .5

        if outputs[m[5]] < outputs[cm[5]]:
            model.e += (outputs[cm[5]] - outputs[m[1]]) ** .5
        else:
            model.e -= (outputs[cm[5]] - outputs[m[1]]) ** .5
