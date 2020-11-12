import pickle
import chess
import chess.pgn
import os
import sys
import random
import chess.svg
import numpy as np

sys.setrecursionlimit(0x100000)

class PalmTree:
    def __init__(self, path):
        self.path = path
        self.white = {}
        self.black = {}
        self.moves = []
        self.gatherData()

    def gatherData(self):
        # creates database based on folder of pgns
        for file in os.listdir(self.path):
            print("reading " + file)
            if (file.endswith('pgn')):
                pgn = open(os.path.join(self.path, file))
                game = chess.pgn.read_game(pgn)
                while game is not None:
                    key = ""
                    i = 0
                    result = game.headers['Result'].strip()
                    for move in game.mainline_moves():
                        i += 1
                        key += str(move) + ','
                        if i == 2:
                            break
                    if result == '1-0':
                        if key in self.white:
                            self.white[key].append(game)
                        else:
                            self.white[key] = []
                            self.white[key].append(game)
                    elif result == '0-1':
                        if key in self.black:
                            self.black[key].append(game)
                        else:
                            self.black[key] = []
                            self.black[key].append(game)
                    else:
                        if key not in self.white and key not in self.black:
                            self.black[key] = []
                            self.white[key] = []
                        elif key not in self.white:
                            self.white[key] = []
                        elif key not in self.black:
                            self.black[key] = []

                        self.white[key].append(game)
                        self.black[key].append(game)
                    try:
                        game = chess.pgn.read_game(pgn)
                    except:
                        game = chess.pgn.read_game(pgn)

    def learn(self):
        for gameKey in self.white:
            for game in self.white:
                board = chess.Board()
                i = 0
                #We're trying to learn from white's victories
                for move in game.mainline_moves():
                    if i % 2 == 0:
                        moves = self.predictMove(board)
                    else:
                        i += 1
                        continue
                    if move in list:
                        print("correct")
                    else:
                        print("wrong")
                    i += 1



    def predictMove(self, board):
        for ()




    def pickOpening(self):
        total = 0
        for key in self.white:
            total += len(self.white[key])
        rand = random.randint(0, total)
        total = 0
        for key in self.white:
            total += len(self.white[key])
            if rand < total:
                return key.split(',')[0]

    def makeMove(self, board):
        if (board.turn == chess.WHITE):
            # white piece decision making
            if (board.fullmove_number == 1):
                #pick an opening
                move = self.pickOpening()
                self.moves.append(board.peek())
                return board
            else:
                self.moves.append(board.peek())
                for key in self.white:
                    print(key)
                    if (key == str(self.moves[0]) + ',' + str(self.moves[1]) + ','):
                        break
                for game in self.white[key]:
                    i = 0
                    for move in game.mainline_moves():
                        if i == len(self.moves):
                            board.push(move)
                            self.moves.append(move)
                            return board
                        if (move != self.moves[i]):
                            break

        else:
            ## if playing the black pieces
            if (len(self.moves) == 1):
                self.moves.append(board.peek())
                defenseOptions = []
                for key in self.black:
                    print(key.split(',')[0])
                    print(self.moves[0])
                    uci = board.parse_san(self.moves[0])
                    if key.split(',')[0] == uci:
                        defenseOptions.append(key.split(',')[1])
                try:
                    move = random.choice(defenseOptions)
                except:
                    #board.push('e5')
                    self.moves.append(board.peek())
                    return board
                uciMove = chess.Move.from_uci(move[0])
                board.push(uciMove)
                self.moves.append(board.peek())
                return board
            else:
                self.moves.append(board.peek())
                for key in self.white:
                    if (key == str(self.moves[0]) + ',' + str(self.moves[1]) + ','):
                        break
                for game in self.white[key]:
                    i = 0
                    for move in game.mainline_moves():
                        if i == len(self.moves):
                            board.push(move)
                            self.moves.append(move)
                            return board
                        if (move != self.moves[i]):
                            break

                for move in board.legal_moves:
                    print('he')

    def createPickle():
        tree = PalmTree(os.path.join(sys.path[0], "games"))
        out = open(os.path.join(sys.path[0], "PalmTree"), 'wb')
        pickle.dump(tree, out)
        out.close()
        print('done')

    def dePickle():
        pick = open(os.path.join(sys.path[0], "PalmTree"), 'rb')
        tree = pickle.load(pick)
        return tree


def play(tree):
    board = chess.Board()

    whiteOrBlack = random.randint(0, 1)
    if whiteOrBlack == 1:
        print("Tree is white")
        tree.makeMove(board)
    while(not board.is_game_over()):
        print(board)
        playerMove = ""
        while 1 == 1:
            playerMove = input('make your move: ')
            try:
                board.push(board.parse_san(playerMove))
                tree.moves.append(playerMove)
                break
            except:
                continue
        tree.makeMove(board)



if __name__ == '__main__':
    tree = PalmTree.dePickle()
    play(tree)
