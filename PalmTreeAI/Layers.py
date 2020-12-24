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
color = None
x = 0

def model(model, inputs, out, depth):
    global outputs
    outputs = {}
    predicts = {}
    print('starting fit')
    for board in inputs:
        inputLayer(model, board, out, depth)

def predict(model, board, depth, l7):
    global predicts
    global color
    color = board.turn
    for move in board.legal_moves:
        predicts[move.uci()] = {}
        board.push(move)
        layer2(board, move)
        layer3(board, move)
        layer4(board, move)
        layer5(board, move)
        layer6(board, 0)
        #if not l7:
            #layer7(model, board, depth)
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
def inputLayer(model, board, out, depth):
    global x
    global outputs
    global color
    x += 1
    print('fit', x)
    color = board.turn
    moves = board.legal_moves
    i = 0
    for move in moves:
        outputs[move.uci()] = {}
        board.push(move)
        layer2(board, move)
        layer3(board, move)
        layer4(board, move)
        layer5(board, move)
        layer6(board, move, 0)
        #layer7(model, board, depth)
        board.pop()
    move = decide(model)
    outputLayer(model, move, out[i])
    i += 1
    outputs = {}

#Layer 2 analyzes the significance of the increase in number of attacks
def layer2(board, move):
    global outputs
    outputs[move.uci()][2] = len(board.attacks(move.to_square))

#Layer 3 analyzes the significance of the decrease in opponent attacks
def layer3(board, move):
    global outputs
    myMove = board.pop()
    oppMove = board.pop()
    board.push(oppMove)
    opAtk1 = len(board.attacks(oppMove.to_square))
    board.push(myMove)
    opAtk2 = len(board.attacks(oppMove.to_square))
    outputs[move.uci()][3] = opAtk1 - opAtk2

#layer 4 checks for checkmate. We know we want checkmate but the machine initially does not!
def layer4(board, move):
    global outputs
    if (board.is_checkmate()):
        outputs[move.uci()][4] = 1
    else:
        outputs[move.uci()][4] = 0

# layer 5 checks for attacks by opponent at move
def layer5(board, move):
    global outputs
    attackers = board.attackers(color, move.to_square)
    outputs[move.uci()][5] = len(attackers)

# layer 6 looks for material advantage
def layer6(board, move, prediction):
    global outputs
    global color
    white = 0
    black = 0
    bk = 0 # knights and bishops need equal value
    i = 0
    while 1:
        i += 1
        pieces = board.pieces(i, chess.WHITE)

        # These if statements suck but they are our means of communicating correct value to the machine
        # If anyone sees a way to do this that doesn't involve these grotesque booleans let me know!
        if i == 2:
            i += 1
            bk = 1
        elif i == 4:
            i = 5
        elif i == 5:
            i = 8
        elif i == 6:
            i = 100

        white += i * len(pieces)
        if i == 100:
            break
        elif i == 8:
            i = 5
        elif i == 5:
            i = 4
        elif (i == 3 and bk):
            i -= 1
            bk = 0

    i = 2
    j = 2
    centerSquares = []
    while 1:
        square = chess.square(i, j)
        centerSquares.append(square)

        j += 1
        if (j == 5):
            if (i == 5):
                break
            j = 2
            i += 1
    for square in centerSquares:
        if board.color_at(square) == chess.WHITE:
            white += 1
        else:
            black += 1
    if not prediction:
        if color == chess.WHITE:
            outputs[move.uci()][6] = (white - black) / 100
        else:
            outputs[move.uci()][6] = (black - white) / 100
    else:
        if not color == chess.WHITE:
            outputs[move.uci()][6] = (white - black) / 100
        else:
            outputs[move.uci()][6] = (black - white) / 100



"""
# layer 7 is a lookahead for disadvantages
def layer7(model, board, depth):
    global outputs
    for i in range(depth):
        opMove = predict(model, board, 0, 1)
        board.push(opMove)
    adv = layer6(board, 1)
    outputs[move.uci()][7] = adv
"""

def decide(model):
    global outputs
    bestMove = None
    for move in outputs:
        outputs[move['sum']] = model.a * outputs[move][2] + model.b * outputs[move][3] + model.c * outputs[move][3] + model.d * outputs[move][4] + model.e * outputs[move][5] + model.f * outputs[move][6] #+ model.g * outputs[move.uci()][7]
        if not bestMove or outputs[move['sum']] > outputs[bestMove['sum']]:
            bestMove = move
    return bestMove

def outputLayer(model, m, cm):
    global outputs
    if (move != cm):
        print("tree wrong :/")
        if outputs[m][1] < outputs[cm][1]:
            model.a += (outputs[cm][1] - outputs[m][1]) ** .5
        else:
            model.a -= (outputs[cm][1] - outputs[m][1]) ** .5

        if outputs[m][2] < outputs[cm][2]:
            model.b += (outputs[cm][2] - outputs[m][2]) ** .5
        else:
            model.b -= (outputs[cm][2] - outputs[m][2]) ** .5

        if outputs[m][3] < outputs[cm][3]:
            model.c += (outputs[cm][3] - outputs[m][3]) ** .5
        else:
            model.c -= (outputs[cm][3] - outputs[m][3]) ** .5

        if outputs[m][4] < outputs[cm][4]:
            model.d += (outputs[cm][4] - outputs[m][4]) ** .5
        else:
            model.d -= (outputs[cm][4] - outputs[m][4]) ** .5

        if outputs[m][5] < outputs[cm][5]:
            model.e += (outputs[cm][5]- outputs[m][5]) ** .5
        else:
            model.e -= (outputs[cm][5] - outputs[m][5]) ** .5

        if outputs[m][6] < outputs[cm][6]:
            model.f += (outputs[cm][6] - outputs[m][6]) ** .5
        else:
            model.f -= (outputs[cm][6] - outputs[m][6]) ** .5

        if outputs[m][7] < outputs[cm][7]:
            model.g += (outputs[cm][7] - outputs[m][7]) ** .5
        else:
            model.g -= (outputs[cm][7] - outputs[m][7]) ** .5

    else:
        print("PalmTree was right!")
