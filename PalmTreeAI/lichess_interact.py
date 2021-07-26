import requests_async as requests
import aiohttp
import json
import time
HEADERS = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer KFhBB3KzFXbUUCYY'
}
class Lichess_Interact:
    async def init(self):
        self.games = []
        self.url = None

    async def make_move(self, move):
        if self.game == None:
            print('no game to make move in')
            return
        url = 'https://lichess.org/api/bot/game/' + str(self.game) + '/move/' + str(move)
        await requests.post(url, headers=HEADERS)
        return

    async def create_game(self):
        data = {
            'rated': 'false',
            'variant': 'standard',
            'color': 'random',
            'ratingRange': ''
        }
        url = 'https://lichess.org/api/challenge/TiredBoiHours'
        session = aiohttp.ClientSession(headers=HEADERS)
        async with session.post(url, json=data) as response:
            body = await response.json()
        await session.close()
        print(body)
        self.game = body['challenge']['id']
        return body

    '''
    async def create_game_with_AI(level):
        data = {
            'level': level,
            'rated': False,
            'variant': 'standard',
            'color': 'random',
            'ratingRange': '',
        }
        url = 'https://lichess.org/api/challenge/TiredBoiHours'
        response = await requests.post(url, data=data, headers=HEADERS)
        self.game = response.challenge.id
    '''

    async def stream(self):
        url = 'https://lichess.org/api/stream/event'
        session = aiohttp.ClientSession(headers=HEADERS)
        while 1:
            async with session.get(url) as response:
                chunk = await response.content.read(0x10000000)
                print(chunk)
                try:
                    chunk = json.loads(chunk)
                except:
                    time.sleep(2)
                    continue
                if chunk['type'] == 'gameStart':
                    break
        await session.close()
        return chunk


    async def read_game_state(self):
        url = 'https://lichess.org/api/bot/game/stream/'+self.game
        session = aiohttp.ClientSession(headers=HEADERS)
        while 1:
            async with session.get(url) as response:
                chunk = await response.content.read(0x10000000)
                print(chunk)
                try:
                    chunk = json.loads(chunk)
                except:
                    time.sleep(2)
                    continue
                return chunk
        await session.close()
        return chunk
