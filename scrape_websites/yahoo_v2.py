#Works but Yahoo is bad
import cloudscraper
from bs4 import BeautifulSoup
import re

def scrape_nhl_odds():
    scraper = cloudscraper.create_scraper()
    url = "https://sports.yahoo.com/nhl/odds/"
    response = scraper.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    game_containers = soup.find_all('div', class_='sixpack')
    games_data = []

    for game in game_containers:
        game_info = {}
        away_team = game.select_one(".sixpack-away-team span.Fw\\(600\\)")
        home_team = game.select_one(".sixpack-home-team span.Fw\\(600\\)")

        if away_team and home_team:
            game_info['away_team'] = away_team.text.strip()
            game_info['home_team'] = home_team.text.strip()
        else:
            continue

        period_time = game.select_one(".C\\(\\#6d7278\\)")
        if period_time:
            game_info['current_time'] = period_time.text.strip()

        away_score = game.select_one(".sixpack-away-team span.Fw\\(800\\)")
        home_score = game.select_one(".sixpack-home-team span.Fw\\(800\\)")

        if away_score and home_score:
            game_info['away_score'] = away_score.text.strip()
            game_info['home_score'] = home_score.text.strip()

        try:
            rows = game.select('table tbody tr')
            if len(rows) >= 2:
                away_cells = rows[0].select('td')
                if len(away_cells) >= 4:
                    away_ml = away_cells[1].get_text(strip=True)
                    if away_ml:
                        game_info['away_moneyline'] = extract_odds(away_ml)
                    away_spread_text = away_cells[2].get_text(strip=True)
                    if away_spread_text:
                        game_info['away_spread'] = extract_odds(away_spread_text)
                    over_text = away_cells[3].get_text(strip=True)
                    if over_text:
                        game_info['over'] = extract_over_under(over_text)

                home_cells = rows[1].select('td')
                if len(home_cells) >= 4:
                    home_ml = home_cells[1].get_text(strip=True)
                    if home_ml:
                        game_info['home_moneyline'] = extract_odds(home_ml)
                    home_spread_text = home_cells[2].get_text(strip=True)
                    if home_spread_text:
                        game_info['home_spread'] = extract_odds(home_spread_text)
                    under_text = home_cells[3].get_text(strip=True)
                    if under_text:
                        game_info['under'] = extract_over_under(under_text)
        except Exception as e:
            print(f"Error parsing odds for {game_info.get('away_team', 'Unknown')} @ {game_info.get('home_team', 'Unknown')}: {e}")

        games_data.append(game_info)

    return games_data

def extract_odds(text):
    if "%" in text:
        match = re.search(r'([+-]\d+)$', text)
        if match:
            return match.group(1)
    match = re.search(r'([+-]\d+)', text)
    if match:
        return match.group(1)
    return text

def extract_over_under(text):
    if "%" in text:
        match = re.search(r'([OU] \d+\.?\d*)', text)
        if match:
            return match.group(1)
    match = re.search(r'([OU] \d+\.?\d*)([+-]\d+)?', text)
    if match:
        if match.group(2):
            return match.group(1) + match.group(2)
        return match.group(1)
    return text

def standardize_team_format(team_name, use_full_names=True):
    nhl_teams = {
        'ANA': 'Ducks', 'ARI': 'Coyotes', 'BOS': 'Bruins', 'BUF': 'Sabres',
        'CGY': 'Flames', 'CAR': 'Hurricanes', 'CHI': 'Blackhawks', 'COL': 'Avalanche',
        'CBJ': 'Blue Jackets', 'DAL': 'Stars', 'DET': 'Red Wings', 'EDM': 'Oilers',
        'FLA': 'Panthers', 'LA': 'Kings', 'LAK': 'Kings', 'MIN': 'Wild',
        'MTL': 'Canadiens', 'NSH': 'Predators', 'NJ': 'Devils', 'NYI': 'Islanders',
        'NYR': 'Rangers', 'OTT': 'Senators', 'PHI': 'Flyers', 'PIT': 'Penguins',
        'SJ': 'Sharks', 'SEA': 'Kraken', 'STL': 'Blues', 'TB': 'Lightning',
        'TOR': 'Maple Leafs', 'VAN': 'Canucks', 'VGK': 'Golden Knights',
        'WSH': 'Capitals', 'WPG': 'Jets', 'UTA': 'Hockey Club'
    }
    reverse_nhl_teams = {v: k for k, v in nhl_teams.items()}

    if team_name in nhl_teams and not use_full_names:
        return team_name
    elif team_name in nhl_teams and use_full_names:
        return nhl_teams[team_name]

    for full_name in reverse_nhl_teams:
        if full_name in team_name:
            if use_full_names:
                return full_name
            else:
                return reverse_nhl_teams[full_name]

    return team_name

def print_game_info(game, use_full_names=True):
    away = standardize_team_format(game.get('away_team', 'Unknown'), use_full_names)
    home = standardize_team_format(game.get('home_team', 'Unknown'), use_full_names)
    print(f"{away} @ {home}")
    if 'away_score' in game and 'home_score' in game:
        print(f"Score: {away} {game['away_score']} - {home} {game['home_score']}")
    if 'current_time' in game:
        print(f"Status: {game['current_time']}")
    print("BETTING ODDS:")
    away_ml = game.get('away_moneyline', 'N/A')
    home_ml = game.get('home_moneyline', 'N/A')
    print(f"Moneyline: {away} {away_ml} | {home} {home_ml}")
    away_spread = game.get('away_spread', 'N/A')
    home_spread = game.get('home_spread', 'N/A')
    if away_spread != 'N/A' and away_spread.startswith('+'):
        away_spread = '+1.5'
    elif away_spread != 'N/A' and away_spread.startswith('-'):
        away_spread = '-1.5'
    if home_spread != 'N/A' and home_spread.startswith('+'):
        home_spread = '+1.5'
    elif home_spread != 'N/A' and home_spread.startswith('-'):
        home_spread = '-1.5'
    print(f"Spread: {away} {away_spread} | {home} {home_spread}")
    over = game.get('over', 'N/A')
    under = game.get('under', 'N/A')
    print(f"Total: Over {over} | Under {under}")
    print("")

games = scrape_nhl_odds()
print(f"Found {len(games)} NHL games\n")
use_full_names = True
for game in games:
    print_game_info(game, use_full_names)
