import requests_async as requests
import aiohttp
import json
import time
import ndjson

HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer KFhBB3KzFXbUUCYY'
}
class Lichess_Interact:
    async def init(self):
        self.games = {}
        self.url = None
        self.session = None

    async def make_move(self, move, game):
        url = 'https://lichess.org/api/bot/game/' + game + '/move/' + str(move)
        async with self.session.post(url) as response:
            r = await response.json()
        return r

    async def accept_challenge(self, challenge):
        # my personal lichess account. Change to play yourself!
        url = 'https://lichess.org/api/challenge/' + challenge + '/accept' 

        async with self.session.post(url) as response:
            body = await response.json()
        print(body)
        return body

    async def create_game(self):
        data = {
            'rated': 'false',
            'variant': 'standard',
            'color': 'random',
            'ratingRange': ''
        }
        # my personal lichess account. Change to play yourself!
        url = 'https://lichess.org/api/challenge/TiredBoiHours' 

        async with self.session.post(url, json=data) as response:
            try:
                body = await response.json()
            except:
                print(response)
                exit()
        print(body)
        self.games.append(body['challenge']['id'])
        return body

    async def stream(self):
        url = 'https://lichess.org/api/stream/event'
        while 1:
            async with self.session.get(url) as response:
                chunk = await response.content.read(0x100000)
                try:
                    chunk = ndjson.loads(chunk)
                    print(chunk)
                except Exception as e:
                    print('ERROR:', e)
                    time.sleep(2)
                    continue
                if len(chunk) > 0:
                    return chunk
                print('waiting for something to happen')
                time.sleep(4)

    async def stream_game_state(self, game):
        url = 'https://lichess.org/api/bot/game/stream/'+game
        async with self.session.get(url) as response:
            chunk = await response.content.read(0x100000)
            print(chunk)
            try:
                chunk = ndjson.loads(chunk)
                print(chunk)
            except Exception as e:
                print('Error parsing game stream:', e)
                exit()
            return chunk
