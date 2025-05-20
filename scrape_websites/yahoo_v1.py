#Works but faulty
import requests
from bs4 import BeautifulSoup
import cloudscraper

bets_url = "https://sports.yahoo.com/nhl/odds/"

bets_response = requests.get(bets_url)
bets_soup = BeautifulSoup(bets_response.text, 'html.parser')

teams_lst = []
records_lst = []
odds_lst = []
livetime_lst = []
livescore_lst = []
pregameodds_lst = []
date_lst = []
game_lst = []
goalies_lst = []
status_lst = []

scraper = cloudscraper.create_scraper()

goalies_url = "https://www.lineups.com/nhl-starting-goalies"
goalies_response = scraper.get(goalies_url)

goalies_soup = BeautifulSoup(goalies_response.text, 'html.parser')


def getGoalies():
    goalies_div = goalies_soup.find_all('span', class_='player-name-col-lg')

    for goalies_tag in goalies_div:
        goalies_lst.append(goalies_tag.get_text(strip=True))


def getStatus():
    status_div = goalies_soup.find_all('span', class_='status-name')

    for status_tag in status_div:
        status_lst.append(status_tag.get_text(strip=True))


def printGoalieInfo():
    getGoalies()
    getStatus()

    for i in range(len(goalies_lst)):
        print(f"{goalies_lst[i]} ({status_lst[i]})")


printGoalieInfo()


def getTeams():
    teams_div = bets_soup.find_all('span', class_='Fw(600) Pend(4px) Ell D(ib) Maw(190px) Va(m)')

    for teams_tag in teams_div:
        if len(teams_tag.get_text(strip=True)) > 3:
            teams_lst.append(teams_tag.get_text(strip=True))


def getRecord():
    records_div = bets_soup.find_all('span', class_='C(dimmed-text) Fz(12px)')

    for records_tag in records_div:
        records_lst.append(records_tag.get_text(strip=True))
        #print(records_tag.get_text(strip=True))


def getOdds():
    odds_div = bets_soup.find_all('span', class_='Lh(19px)')

    for odds_tag in odds_div:
        odds_lst.append(odds_tag.get_text(strip=True))
        #print(odds_tag.get_text(strip=True))


def getLiveTime():
    livetime_div = bets_soup.find_all('span', class_='C(#6d7278) Fz(14px) smartphone_Fz(12px)')

    for livetime_tag in livetime_div:
        livetime_lst.append(livetime_tag.get_text(strip=True))
        #print(livetime_tag.get_text(strip=True))

def getLiveScore():
    livescore_div = bets_soup.find_all('span', class_='Fw(800) D(n) D(ib)!--medPhone Fl(end) Maw(30px) Pend(12px)')

    for livescore_tag in livescore_div:
        livescore_lst.append(livescore_tag.get_text(strip=True))
        #print(livescore_tag.get_text(strip=True))


def getPregameOdds():
    pregameodds_div = bets_soup.find_all('td', class_='Pt(16px)')

    for pregameodds_tag in pregameodds_div:
        pregameodds_lst.append(pregameodds_tag.get_text(strip=True))
        #print(pregameodds_tag.get_text(strip=True))

def printBetInfo():
    getOdds()
    getTeams()
    getLiveTime()
    getLiveScore()

    print("\n\n\n\n\n\n")

    # Pair live scores and live times with teams
    for i, team in enumerate(teams_lst):
        start = i * 5  # 5 odds per team
        end = start + 5

        # Calculate the live info index (each game has 2 teams, so live time is shared)
        live_info_index = i // 2  # Integer division to group teams into games

        # Get live time (shared for both teams in a game)
        live_time = livetime_lst[live_info_index] if live_info_index < len(livetime_lst) else "N/A"

        # Get live score (unique for each team)
        live_score = livescore_lst[i] if i < len(livescore_lst) else "N/A"

        # Print team info
        print(f"{team} {live_score} {live_time}")

        # Check if there are any odds left for this team
        if start < len(odds_lst):
            # Get the available odds for this team
            team_odds = odds_lst[start:end] if end <= len(odds_lst) else odds_lst[start:]

            # Map the odds to their respective fields
            money_line = team_odds[0] if len(team_odds) > 0 else "N/A"
            point_spread = team_odds[1] if len(team_odds) > 1 else "N/A"
            point_spread_odds = team_odds[2] if len(team_odds) > 2 else "N/A"
            total_points = team_odds[3] if len(team_odds) > 3 else "N/A"
            total_points_odds = team_odds[4] if len(team_odds) > 4 else "N/A"

            # Print the odds
            print(f"- Money Line: ({money_line})")
            print(f"- Point Spread: {point_spread} ({point_spread_odds})")
            print(f"- Total Points: {total_points} ({total_points_odds})")
        else:
            # Handle cases where there are no odds at all for this team
            print("- Money Line: N/A")
            print("- Point Spread: N/A")
            print("- Total Points: N/A")
        print()

printBetInfo()

def getLiveScore():
    livescore_div = bets_soup.find_all('div', class_='bet-packs-wrapper')

    for livescore_tag in livescore_div:
        livescore = livescore_tag.get_text(strip=True)

        print(livescore)
        #print(livescore_tag.get_text(strip=True))

#getLiveScore()
