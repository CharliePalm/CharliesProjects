import chess
import asyncio
import aiohttp
import time
import numpy as np
from data_organization import data_organization
from creator import PalmTree
from lichess_interact import Lichess_Interact
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer KFhBB3KzFXbUUCYY'
}
async def main():
    print('creating challenge')
    await tree.lichess.create_game()
    board = chess.Board()
    moves = np.array([])

    r = await tree.lichess.stream()
    r = await tree.lichess.read_game_state()
    if r['white']['name'] == 'PalmTeeBot':
        whiteOrBlack = True
        move = tree.make_move(board, whiteOrBlack)
        await tree.lichess.make_move(move)
        board.push(chess.Move.from_uci(move))
        moves = np.array([move], dtype=str)
    else:
        whiteOrBlack = False

    while 1:
        stream = await tree.lichess.read_game_state()
        if stream['state']['status'] != 'started':
            print('Good game!')
            break
        new_moves = np.array(stream['state']['moves'].split(), dtype=str)
        if len(new_moves) == len(moves):
            continue
        moves = new_moves
        print(moves)
        move = tree.make_move(board, whiteOrBlack)
        await tree.lichess.make_move(move)
        board.push(chess.Move.from_uci(move))
        np.append(moves, move)

if __name__ == '__main__':
    print('getting PalmTree ready')
    tree = data_organization.dePickle('models/PalmTree')
    tree.lichess = Lichess_Interact()
    tree.lichess.session = aiohttp.ClientSession(headers=HEADERS)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
