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
        self.session = None

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

        async with self.session.post(url, json=data) as response:
            try:
                body = await response.json()
            except:
                print(response)
                exit()
        print(body)
        self.game = body['challenge']['id']
        return body

    async def stream(self):
        url = 'https://lichess.org/api/stream/event'
        while 1:
            async with self.session.get(url) as response:
                chunk = await response.content.read(0x10000000)
                print(chunk)
                try:
                    chunk = json.loads(chunk)
                except Exception as e:
                    print(e)
                    time.sleep(2)
                    continue
                return chunk

    async def read_game_state(self):
        url = 'https://lichess.org/api/bot/game/stream/'+self.game
        while 1:
            async with self.session.get(url) as response:
                chunk = await response.content.read(0x10000000)
                print(chunk)
                try:
                    chunk = json.loads(chunk)
                except:
                    print('error reading chunk')
                    time.sleep(2)
                    continue
                return chunk
        return chunk
