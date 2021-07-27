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
async def main(tree):
    tree.lichess.games = {}
    tree.lichess.session = aiohttp.ClientSession(headers=HEADERS)
    while 1:
        events = await tree.lichess.stream()
        for ev in events:
            if ev['type'] == 'challenge':
                id = ev['challenge']['id']
                await tree.lichess.accept_challenge(id)
            elif ev['type'] == 'gameFinish':
                del ev['game']['id']
                continue
            else:
                id = ev['game']['id']
            if id not in tree.lichess.games:
                tree.lichess.games[id] = chess.Board()
            await make_move(tree, id)
        print('waiting for events')
        time.sleep(3)
            
async def make_move(tree, id):
    r = await tree.lichess.stream_game_state(id)
    
    moves = r[0]['state']['moves'].split()
    white = False
    if r[0]['white']['name'] == 'PalmTreeBot':
        white = True
    if (len(moves) % 2 != 0 and white) or (len(moves) % 2 == 0 and not white):
        return
    if len(moves) != 0:
        tree.lichess.games[id].push(chess.Move.from_uci(moves[len(moves)-1]))
    print('\n\n MAKING MOVE \n\n')
    move = tree.make_move(tree.lichess.games[id], white)
    tree.lichess.games[id].push(chess.Move.from_uci(move))
    await tree.lichess.make_move(move, id)




if __name__ == '__main__':
    print('getting PalmTree ready')
    tree = data_organization.dePickle('models/PalmTree')
    tree.lichess = Lichess_Interact()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(tree))
