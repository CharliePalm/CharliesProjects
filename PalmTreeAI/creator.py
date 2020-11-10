import pickle
import chess
import chess.pgn
import os
import sys
sys.setrecursionlimit(0x100000)

class PalmTree:
    def __init__(self, path):
        self.path = path
        self.white = {}
        self.black = {}
        self.analyze()

    def analyze(self):
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
                        key += str(move)
                        if i == 2:
                            break
                    if result == '1-0':
                        self.white[key] = game
                    elif result == '0-1':
                        self.black[key] = game
                    else:
                        self.white[key] = game
                        self.black[key] = game
                    try:
                        game = chess.pgn.read_game(pgn)
                    except:
                        game = chess.pgn.read_game(pgn)
    def thinkAboutMove(self):
        print('neat')


def createPickle():
    tree = PalmTree('/Users/chuckpalm/Documents/git/CharliesProjects/PalmTreeAI/Games')
    print("finished creating object:")
    out = open("/Users/chuckpalm/Documents/git/CharliesProjects/PalmTreeAI/PalmTree", 'wb')
    print(tree.black)
    print(tree.white)
    pickle.dump(tree, out)
    out.close()
    print('done')

def dePickle():
    pick = open('/Users/chuckpalm/Documents/git/CharliesProjects/PalmTreeAI/PalmTree', 'rb')
    tree = pickle.load(pick)
    return tree


if __name__ == '__main__':
    tree = dePickle()
    board = chess.Board()
