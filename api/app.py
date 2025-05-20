from flask import Flask, jsonify, render_template, request
import requests
from bs4 import BeautifulSoup
import sys
import os
sys.path.append(os.path.dirname(__file__))

from teams_info import team_logos, team_abbreviations
import os

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../static')
)

def scrape_nhl_odds():
    bets_url = "https://sportsdata.usatoday.com/hockey/nhl/odds"
    bets_response = requests.get(bets_url)
    bets_soup = BeautifulSoup(bets_response.text, 'html.parser')
    game_containers = bets_soup.find_all('div', class_=lambda c: c and '__2kWqut' in c)
    parsed_games = []

    for container in game_containers:
        game_data = {}
        team_items = container.select('ul[class*="__R0o3Uy"] > li')
        if len(team_items) >= 2:
            start_index = 0
            if team_items[0].select_one('ul[class*="__4eeT9w"]'):
                start_index = 1
            if len(team_items) >= start_index + 2:
                away_team_name = team_items[start_index].select_one('span[class*="__jer7Rp"]')
                home_team_name = team_items[start_index + 1].select_one('span[class*="__jer7Rp"]')
                if away_team_name and home_team_name:
                    raw_away = away_team_name.text.strip()
                    raw_home = home_team_name.text.strip()
                    game_data['away_team'] = team_abbreviations.get(raw_away, raw_away)
                    game_data['home_team'] = team_abbreviations.get(raw_home, raw_home)
                away_record = team_items[start_index].select_one('span[class*="__QA1t2T"]')
                home_record = team_items[start_index + 1].select_one('span[class*="__QA1t2T"]')
                if away_record and home_record:
                    game_data['away_record'] = away_record.text.strip()
                    game_data['home_record'] = home_record.text.strip()
                away_score = team_items[start_index].select_one('span[class*="__sy7S-6"] span')
                home_score = team_items[start_index + 1].select_one('span[class*="__sy7S-6"] span')
                if away_score and home_score:
                    game_data['away_score'] = away_score.text.strip()
                    game_data['home_score'] = home_score.text.strip()

        # First check for status in the urWQNR class element (most common location)
        status_element = container.select_one('p[class*="__urWQNR"]')
        if status_element:
            status_text = status_element.text.strip()

            # Handle "End P_" format
            if status_text.startswith('End P'):
                game_data['current_period'] = status_text.split('See')[0].strip()
            elif 'Live P' in status_text:
                # Remove the "Live " prefix and split into parts (if there are spaces)
                period_parts = status_text.replace('Live ', '').split(' ')
                if len(period_parts) > 0:
                    # Remove any accidental "See" text
                    s = period_parts[0].replace("See", "")
                    # If the string is longer than 5 characters, assume the last five characters are the time.
                    if len(s) > 5:
                        # Everything before the final five characters is the period (e.g., "P1")
                        game_data['current_period'] = s[:-5]
                        # The final five characters represent the time (e.g., "13:10")
                        game_data['time_remaining'] = s[-5:]
                    else:
                        # Fallback if the string is too short (this path is less likely to be used).
                        period_part = s.split(':')[0]
                        game_data['current_period'] = period_part
                        if ':' in s:
                            time_part = s.split(':', 1)[1]
                            time_part = ''.join(c for c in time_part if c.isdigit() or c == ':')
                            game_data['time_remaining'] = time_part
            elif 'FINAL' in status_text:
                if 'OT' in status_text:
                    game_data['current_period'] = 'FINAL OT'
                elif 'SO' in status_text:
                    game_data['current_period'] = 'FINAL SO'
                else:
                    game_data['current_period'] = 'FINAL'

        # If we still don't have a current_period, search all strings in the container
        if 'current_period' not in game_data:
            status_texts = [elem.strip() for elem in container.find_all(string=True) if elem.strip()]
            for text in status_texts:
                if text.startswith('End P'):
                    game_data['current_period'] = text.split('See')[0].strip()
                    break
                elif 'FINAL' in text:
                    if 'OT' in text:
                        game_data['current_period'] = 'FINAL OT'
                    elif 'SO' in text:
                        game_data['current_period'] = 'FINAL SO'
                    else:
                        game_data['current_period'] = 'FINAL'
                    break
                elif 'Live P' in text:
                    parts = text.replace('Live ', '').split(' ')
                    period_part = parts[0].split(':')[0].replace('See', '')
                    game_data['current_period'] = period_part
                    if ':' in parts[0]:
                        time_part = parts[0].split(':', 1)[1]
                        time_part = ''.join(c for c in time_part if c.isdigit() or c == ':')
                        game_data['time_remaining'] = time_part
                    break
                elif text.startswith('P') and ':' in text:
                    period_part = text.split(':')[0]
                    game_data['current_period'] = period_part
                    time_part = text.split(':', 1)[1]
                    time_part = ''.join(c for c in time_part if c.isdigit() or c == ':')
                    game_data['time_remaining'] = time_part
                    break

        # One more place to check for game status
        status_p_element = container.select_one('p[class*="__9aFieZX"]')
        if status_p_element and 'current_period' not in game_data:
            status_text = status_p_element.text.strip()
            if status_text.startswith('End P'):
                game_data['current_period'] = status_text.split('See')[0].strip()
            elif status_text.startswith('P') and ':' in status_text:
                period_part = status_text.split(':')[0]
                game_data['current_period'] = period_part
                time_part = status_text.split(':', 1)[1]
                time_part = ''.join(c for c in time_part if c.isdigit() or c == ':')
                game_data['time_remaining'] = time_part

        # Also check table headers for game status
        table_header = container.select_one('th a div div p[class*="__urWQNR"]')
        if table_header and 'current_period' not in game_data:
            status_text = table_header.text.strip()
            if status_text.startswith('End P'):
                game_data['current_period'] = status_text
            elif 'Live P' in status_text or 'FINAL' in status_text:
                game_data['current_period'] = status_text

        odds_table = container.find('table', class_=lambda c: c and '__xBNxWw' in c)
        if odds_table:
            rows = odds_table.find_all('tr')
            if len(rows) >= 3:
                if 'away_team' not in game_data or 'home_team' not in game_data:
                    away_name_cell = rows[1].select_one('td:first-child')
                    home_name_cell = rows[2].select_one('td:first-child')
                    if away_name_cell and home_name_cell:
                        away_team_text = away_name_cell.text.strip()
                        home_team_text = home_name_cell.text.strip()
                        if away_team_text and 'away_team' not in game_data:
                            game_data['away_team'] = away_team_text
                        if home_team_text and 'home_team' not in game_data:
                            game_data['home_team'] = home_team_text

                away_cells = rows[1].find_all('td')
                if len(away_cells) >= 4:
                    spread_cell = away_cells[1].select_one('span[class*="__p7TUuY"]')
                    if spread_cell:
                        spread_value = spread_cell.select_one('b')
                        spread_odds = spread_cell.find('span')
                        if spread_value:
                            game_data['away_spread'] = spread_value.text.strip()
                            is_winner = spread_value.get('class') and any(
                                '__FI-o3p' in c for c in spread_value.get('class', []))
                            game_data['away_spread_winner'] = is_winner
                        if spread_odds:
                            game_data['away_spread_odds'] = spread_odds.text.strip()
                    moneyline_cell = away_cells[2].select_one('span[class*="__p7TUuY"] b')
                    if moneyline_cell:
                        game_data['away_moneyline'] = moneyline_cell.text.strip()
                        is_winner = moneyline_cell.get('class') and any(
                            '__FI-o3p' in c for c in moneyline_cell.get('class', []))
                        game_data['away_moneyline_winner'] = is_winner
                    total_cell = away_cells[3].select_one('span[class*="__p7TUuY"]')
                    if total_cell:
                        over_value = total_cell.select_one('b')
                        over_odds = total_cell.find('span')
                        if over_value:
                            game_data['over_value'] = over_value.text.strip().replace('O ', '')
                            is_winner = over_value.get('class') and any(
                                '__FI-o3p' in c for c in over_value.get('class', []))
                            game_data['over_winner'] = is_winner
                        if over_odds:
                            game_data['over_odds'] = over_odds.text.strip()

                home_cells = rows[2].find_all('td')
                if len(home_cells) >= 4:
                    spread_cell = home_cells[1].select_one('span[class*="__p7TUuY"]')
                    if spread_cell:
                        spread_value = spread_cell.select_one('b')
                        spread_odds = spread_cell.find('span')
                        if spread_value:
                            game_data['home_spread'] = spread_value.text.strip()
                            is_winner = spread_value.get('class') and any(
                                '__FI-o3p' in c for c in spread_value.get('class', []))
                            game_data['home_spread_winner'] = is_winner
                        if spread_odds:
                            game_data['home_spread_odds'] = spread_odds.text.strip()
                    moneyline_cell = home_cells[2].select_one('span[class*="__p7TUuY"] b')
                    if moneyline_cell:
                        game_data['home_moneyline'] = moneyline_cell.text.strip()
                        is_winner = moneyline_cell.get('class') and any(
                            '__FI-o3p' in c for c in moneyline_cell.get('class', []))
                        game_data['home_moneyline_winner'] = is_winner
                    total_cell = home_cells[3].select_one('span[class*="__p7TUuY"]')
                    if total_cell:
                        under_value = total_cell.select_one('b')
                        under_odds = total_cell.find('span')
                        if under_value:
                            game_data['under_value'] = under_value.text.strip().replace('U ', '')
                            is_winner = under_value.get('class') and any(
                                '__FI-o3p' in c for c in under_value.get('class', []))
                            game_data['under_winner'] = is_winner
                        if under_odds:
                            game_data['under_odds'] = under_odds.text.strip()

        if 'away_team' not in game_data or 'home_team' not in game_data:
            team_rows = container.select('tr')
            if len(team_rows) >= 3:
                for i, row in enumerate(team_rows[1:3], 1):
                    team_cell = row.select_one('td[class*="__PCxnHI"]')
                    if team_cell:
                        team_name_elem = team_cell.select_one('div[class*="__7dtF2Y"] div')
                        team_record_elem = team_cell.select_one('span[class*="__qxdHiw"]')
                        if team_name_elem:
                            if i == 1:
                                game_data['away_team'] = team_name_elem.text.strip()
                            else:
                                game_data['home_team'] = team_name_elem.text.strip()
                        if team_record_elem:
                            record_text = team_record_elem.text.strip()
                            if i == 1:
                                game_data['away_record'] = record_text.split('(')[0].strip()
                            else:
                                game_data['home_record'] = record_text.split('(')[0].strip()

        parsed_games.append(game_data)

    return parsed_games

# Helper function to get team logo URL
def get_team_logo(team_name):
    # First check if the full team name is in the dictionary
    if team_name in team_logos:
        return team_logos[team_name]
    
    # Try to find the team name by matching parts
    for key in team_logos:
        if key in team_name:
            return team_logos[key]
    
    # Look for abbreviations
    for abbr, name in team_abbreviations.items():
        if abbr in team_name or team_name in name:
            return team_logos.get(name, "")
    
    # Extract the first word from the team name
    first_word = team_name.split()[0]
    if first_word in team_logos:
        return team_logos[first_word]
    
    # Check for special cases
    if "Blues" in team_name:
        return team_logos.get("St. Louis", "")
    elif "Kraken" in team_name:
        return team_logos.get("Seattle", "")
    elif "Rangers" in team_name:
        return team_logos.get("N.Y. Rangers", "")
    elif "Islanders" in team_name:
        return team_logos.get("N.Y. Islanders", "")
    elif "Golden Knights" in team_name or "VGK" in team_name:
        return team_logos.get("Vegas", "")
    elif "Lightning" in team_name:
        return team_logos.get("Tampa Bay", "")
    elif "Maple Leafs" in team_name:
        return team_logos.get("Toronto", "")
    elif "Red Wings" in team_name:
        return team_logos.get("Detroit", "")
    elif "Sharks" in team_name:
        return team_logos.get("San Jose", "")
    elif "Kings" in team_name:
        return team_logos.get("Los Angeles", "")
    elif "Capitals" in team_name:
        return team_logos.get("Washington", "")
    
    # Return a default logo or empty string if no match is found
    return ""

# Format game data for display
def format_game_data(game):
    formatted_data = {}
    
    # Basic game info
    if 'away_team' in game and 'home_team' in game:
        away_team = game['away_team']
        home_team = game['home_team']
        formatted_data['matchup'] = f"{away_team} @ {home_team}"
        
        # Add team logos
        formatted_data['away_logo'] = get_team_logo(away_team)
        formatted_data['home_logo'] = get_team_logo(home_team)
        formatted_data['away_team'] = away_team
        formatted_data['home_team'] = home_team
    
    # Status information
    if 'current_period' in game:
        status = game['current_period']
        if 'time_remaining' in game:
            status += f" {game['time_remaining']}"
        formatted_data['status'] = status
    
    # Score information
    if 'away_score' in game and 'home_score' in game:
        formatted_data['score'] = f"{game['away_score']} - {game['home_score']}"
        formatted_data['away_score'] = game['away_score']
        formatted_data['home_score'] = game['home_score']
    
    # Betting information
    if 'away_moneyline' in game:
        formatted_data['away_ml'] = game['away_moneyline']
        if game.get('away_moneyline_winner', False):
            formatted_data['away_ml_winner'] = True
    
    if 'home_moneyline' in game:
        formatted_data['home_ml'] = game['home_moneyline']
        if game.get('home_moneyline_winner', False):
            formatted_data['home_ml_winner'] = True
    
    # Spread information
    if 'away_spread' in game:
        spread = game['away_spread']
        if 'away_spread_odds' in game:
            spread += f" ({game['away_spread_odds']})"
        formatted_data['away_spread'] = spread
        if game.get('away_spread_winner', False):
            formatted_data['away_spread_winner'] = True
    
    if 'home_spread' in game:
        spread = game['home_spread']
        if 'home_spread_odds' in game:
            spread += f" ({game['home_spread_odds']})"
        formatted_data['home_spread'] = spread
        if game.get('home_spread_winner', False):
            formatted_data['home_spread_winner'] = True
    
    # Over/Under information
    if 'over_value' in game:
        over = f"O {game['over_value']}"
        if 'over_odds' in game:
            over += f" ({game['over_odds']})"
        formatted_data['over'] = over
        formatted_data['over_value'] = game['over_value']
        if game.get('over_winner', False):
            formatted_data['over_winner'] = True
    
    if 'under_value' in game:
        under = f"U {game['under_value']}"
        if 'under_odds' in game:
            under += f" ({game['under_odds']})"
        formatted_data['under'] = under
        formatted_data['under_value'] = game['under_value']
        if game.get('under_winner', False):
            formatted_data['under_winner'] = True
    
    # Team records
    if 'away_record' in game:
        formatted_data['away_record'] = game['away_record']
    if 'home_record' in game:
        formatted_data['home_record'] = game['home_record']
    
    # Add prediction based on moneyline winner if available
    if game.get('away_moneyline_winner', False):
        formatted_data['prediction'] = game['away_team']
    elif game.get('home_moneyline_winner', False):
        formatted_data['prediction'] = game['home_team']
    
    return formatted_data

@app.route('/')
def index():
    games = scrape_nhl_odds()
    formatted_games = [format_game_data(game) for game in games if game]
    return render_template('index.html', games=formatted_games)

@app.route('/api/odds')
def get_odds_api():
    games = scrape_nhl_odds()
    return jsonify(games)

@app.route('/api/formatted-odds')
def get_formatted_odds_api():
    games = scrape_nhl_odds()
    formatted_games = [format_game_data(game) for game in games if game]
    return jsonify(formatted_games)

if __name__ == '__main__':
    app.run(debug=True)
