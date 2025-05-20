#Does not work, changed their HTML
import requests
from bs4 import BeautifulSoup
import json

bets_url = "https://sportsdata.usatoday.com/hockey/nhl/odds"
bets_response = requests.get(bets_url)
bets_soup = BeautifulSoup(bets_response.text, 'html.parser')

def get_games():
    teams_lst = []
    bets_lst = []
    scores_lst = []
    finals_lst = []
    period_time_list = []

    def getBets():
        bets_div = bets_soup.find_all('span', class_='class-p7TUuYs class-SM1nKPx class-hpKC2HT class-SM1nKPx')
        for bets_tag in bets_div:
            bets_lst.append(bets_tag.get_text(strip=True))

    def getTeams():
        teams_div = bets_soup.find_all('span', class_='class-jer7RpM')
        for teams_tag in teams_div:
            teams_lst.append(teams_tag.get_text(strip=True))

    def getPeriodTime():
        for period_div in bets_soup.find_all('p', class_='class-urWQNRe class-Nzz35dC class-uv22YEH'):
            period_text = period_div.get_text(strip=True, separator=" ")
            time_span = period_div.find('span', class_='class-yeZhSab')
            time_text = time_span.get_text(strip=True) if time_span else ""
            period_time = f"{period_text} {time_text}".strip()
            if "See Game Summary" in period_text:
                index_of_see = period_time.find(" See")
                period_time = period_time[:index_of_see]

            period_time_list.append(period_time)

    def getScores():
        scores_div = bets_soup.find_all('span', class_='class-sy7S-6k class-LhLiKm6 class-Eqj6PbD')
        scores_div2 = bets_soup.find_all('span', class_='class-sy7S-6k class-37MkIom class-LhLiKm6')
        for x, y in zip(scores_div, scores_div2):
            scores_lst.append(f"{x.get_text(strip=True)}-{y.get_text(strip=True)}")

    def getFinals():
        date_div = bets_soup.find_all('p', class_='class-urWQNRe class-8ygQElb')
        for date_tag in date_div:
            date = date_tag.get_text(strip=True).replace("-See Game Summary", "")
            finals_lst.append(date)

    getBets()
    getTeams()
    getPeriodTime()
    getScores()
    getFinals()

    games = []
    final_index = 0
    score_index = 0

    for i in range(0, len(teams_lst) - 1, 2):
        # Determine if the game is completed
        status = period_time_list[i // 2] if i // 2 < len(period_time_list) else (
            finals_lst[final_index] if final_index < len(finals_lst) else "N/A")
        is_completed = "See Game Summary" in status

        # Assign the score only if the game is completed
        if is_completed:
            score = scores_lst[score_index] if score_index < len(scores_lst) else "N/A"
            score_index += 1
        else:
            score = "N/A"

        game = {
            "teams": [teams_lst[i], teams_lst[i + 1]],
            "score": score,
            "odds": {
                "spread": [
                    bets_lst[i * 3] if i * 3 < len(bets_lst) else "N/A",
                    bets_lst[i * 3 + 3] if i * 3 + 3 < len(bets_lst) else "N/A"
                ],
                "moneyline": [
                    bets_lst[i * 3 + 1] if i * 3 + 1 < len(bets_lst) else "N/A",
                    bets_lst[i * 3 + 4] if i * 3 + 4 < len(bets_lst) else "N/A"
                ],
                "total": [
                    bets_lst[i * 3 + 2] if i * 3 + 2 < len(bets_lst) else "N/A",
                    bets_lst[i * 3 + 5] if i * 3 + 5 < len(bets_lst) else "N/A"
                ]
            },
            "status": status
        }
        games.append(game)

        if game["status"] in finals_lst:
            final_index += 1

    return json.dumps(games, indent=4)

print(get_games())
