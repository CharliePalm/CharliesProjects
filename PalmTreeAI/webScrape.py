from bs4 import BeautifulSoup
import requests
import urllib

players = []
r = requests.get('https://www.chess.com/games/bobby-fischer')
text = r.text
soup = BeautifulSoup(text, 'html.parser')
