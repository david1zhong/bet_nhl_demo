#Disfunctional
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

#date = "20250319"
#bets_url = f"https://www.cbssports.com/nhl/expert-picks/{date}/"
bets_url = "https://www.cbssports.com/nhl/expert-picks/"

odds = []
predicted_overs = []
overs = []
names = []
prediction = []
scores = []

bets_response = requests.get(bets_url)
bets_soup = BeautifulSoup(bets_response.text, 'html.parser')


def getOdds():
    odds_div = bets_soup.find_all('div', class_='game-odds')
    count = 1

    for odds_tag in odds_div:
        odds_text = odds_tag.get_text(strip=True)

        if count % 3 == 0:
            predicted_overs.append(odds_text)
            overs.append(odds_text[1:])

        else:
            odds.append(odds_text)

        count += 1


def getWinnerPrediction():
    prediction_div = bets_soup.find_all('div', class_='expert-spread 0')

    for team_tag in prediction_div:
        team_name = team_tag.get_text(strip=True)

        team_name = team_name.replace(" ", "")
        team_name = team_name.replace("\n", "")
        team_name = team_name[:-4] + " " + team_name[-4:]
        prediction.append(team_name)


def getTeams():
    name_div = bets_soup.find_all('span', class_='team')

    for team_tag in name_div:
        team_name = team_tag.get_text(strip=True)
        names.append(team_name)


def getScore():
    score_div = bets_soup.find_all('span', class_='score')

    for score_tag in score_div:
        score = score_tag.get_text(strip=True)
        scores.append(score)

    while len(scores) < len(names):
        scores.append("")


def printOdds():
    getOdds()
    getWinnerPrediction()
    getTeams()
    getScore()

    for i in range(len(names)):
        print(f"{names[i]}: {scores[i]} ({odds[i]})")

        if i % 2 != 0:
            print(f"Over: {overs[i // 2]}, Predicted: {predicted_overs[i // 2]}")
            print(prediction[i // 2])
            print()


printOdds()
