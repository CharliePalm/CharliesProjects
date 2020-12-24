import pickle
import chess
import chess.pgn
import chess.svg
import os
import sys
import random
import chess.svg
import numpy as np
import Layers

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
                if iter < 5:
                    if (iter == 0):
                        opening = move
                        if not self.openings[opening]:
                            self.openings[opening] = {}
                    elif (iter <= 4):
                        if iter == 1:
                            self.openings[opening].append([move])
                            #defense indicates index
                            defense = len(self.openings[opening]) - 1
                        else:
                            self.openings[opening][defense].append(move)
                    iter += 1
                    board.push(move)
                    continue

                elif iter % 2 != 0:
                    board.push(move)
                    iter += 1
                    continue


                self.data.append(board)
                board.push(move)
                self.outputs.append(move)
                iter += 1
        else:
            for move in game.mainline_moves():
                if iter < 5:
                    if (iter == 0):
                        defense = move
                        if not self.defenses[defense]:
                            self.defenses[defense] = {}
                    elif iter <= 5:
                        if iter == 1:
                            self.openings[defense].append([move])
                            #opening indicates index
                            opening = len(self.openings[defense]) - 1
                        else:
                            self.openings[defense][opening].append(move)
                    iter += 1
                    board.push(move)
                    continue

                elif iter % 2 != 0:
                    board.push(move)
                    iter += 1
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

    def dePickle(name):
        pick = open(os.path.join(sys.path[0], name), 'rb')
        tree = pickle.load(pick)
        return tree


class PalmTree:
    def __init__(self, data, depth):
        self.openings = data.openings
        self.defenses = data.defenses
        self.a = 1
        self.b = 1
        self.c = 1
        self.d = 1
        self.e = 1
        self.f = 1
        self.g = 1
        Layers.model(self, pickle.data, pickle.outputs, depth)
        out = open(os.path.join(os.getcwd(), '/PalmTree'), 'wb')
        pickle.dump(self, out)
        out.close

    def makeMove(self, board):
        move = None
        if (len(stack = board.move_stack()) < 5):
            if (board.turn == chess.WHITE):
                if (len(stack) == 0):
                    for key in self.openings:
                        total = total + len(openings[key])

                    pick = random.randint(total)
                    total = 0
                    for key in self.openings:
                        total = total + len(openings[key])
                        if (pick < total):
                            move = key
            else:
                moves = []
                for move in stack:
                    moves.append(stack.pop())
                i = len(moves) - 1
                if moves[len(moves) - 1] in self.openings:
                    opening = self.openings[moves[0]]
                else:
                    Layers.predict(self, board, 0, 0)
                    return
                for z in range(len(move)):
                    i += 1

        else:
            move = Layers.predict(self, board)
        board.push(move)
        return board

"""
    def pickleAI(self):
        out = open(os.path.join(os.getcwd(), name), 'wb')
        pickle.dump(self, out)
        out.close()
        print('done')
"""

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
            chess.svg.board(board, orientation=chess.BLACK)
        else:
            chess.svg.board(board, orientation=chess.WHITE)
        while 1:
            userInput = input("\n")
            try:
                board.push(userInput)
                break
            except:
                continue

        board = tree.makeMove(board)

def model(data, depth):
    tree = PalmTree(data, depth)
    tree.pickleAI()
    play(tree)

if __name__ == '__main__':
    data = dataPool.createPickle((os.getcwd() + '/PalmTreeAI/Games'), 'data')
    data = dataPool.dePickle('data')
    model(data, 3)
