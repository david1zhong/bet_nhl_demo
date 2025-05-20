#ESPN is no good
import requests
from bs4 import BeautifulSoup

bets_url = "https://www.espn.com/nhl/odds"

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/117.0"
}

bets_response = requests.get(bets_url, headers=headers)
bets_soup = BeautifulSoup(bets_response.text, 'html.parser')

lst = []

teams_div = bets_soup.find_all('a', {'data-testid': 'prism-linkbase'})
#teams_div = bets_soup.find_all('div', {'data-testid': 'OddsCell'})


for teams_tag in teams_div:
    if teams_tag.get_text(strip=True) == "Looking for NHL futures?":
        break

    lst.append(teams_tag.get_text(strip=True))

#game_times = [a.text for a in bets_soup.find_all('a', {'data-game-link': 'true'})]

for i in range(len(lst)):
    print(f"{i}: {lst[i]}")

print(lst)


#for i in range(0, len(lst), 5):
#    print(lst[i:i+5])
