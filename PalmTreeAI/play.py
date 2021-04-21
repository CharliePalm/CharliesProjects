from data_organization import data_organization
import pickle
import chess
import chess.pgn
import chess.svg
import sys
import random
from creator import PalmTree
def play(tree):
    board = chess.Board()
    whiteOrBlack = random.choice([0, 1])

    if (whiteOrBlack):
        move = tree.make_move(board, whiteOrBlack)
        board.push(chess.Move.from_uci(move))

    userInput = ''
    while (userInput != 'q' or userInput != 'Q'):
        print(board)


        while 1:
            userInput = input("\n")
            try:
                board.push(chess.Move.from_uci(userInput))
                break
            except:
                print('invalid move')
                continue
        print(board)
        move = tree.make_move(board, whiteOrBlack)
        print('I think I will play', move)
        board.push(chess.Move.from_uci(move))


if __name__=='__main__':

    m = input('which model of albert would you like to play? ')
    tree = data_organization.dePickle('models/Albert_model_' + m)
    play(tree)
