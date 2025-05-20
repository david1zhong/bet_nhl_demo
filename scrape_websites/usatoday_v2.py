import requests
from bs4 import BeautifulSoup

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
                    game_data['away_team'] = away_team_name.text.strip()
                    game_data['home_team'] = home_team_name.text.strip()
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

        status_element = container.select_one('p[class*="__urWQNR"]')
        if status_element:
            status_text = status_element.text.strip()
            if 'Live P' in status_text:
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

        if 'current_period' not in game_data:
            status_texts = [elem.strip() for elem in container.find_all(string=True) if elem.strip()]
            for text in status_texts:
                if 'FINAL' in text:
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

        status_p_element = container.select_one('p[class*="__9aFieZX"]')
        if status_p_element and 'current_period' not in game_data:
            status_text = status_p_element.text.strip()
            if status_text.startswith('P') and ':' in status_text:
                period_part = status_text.split(':')[0]
                game_data['current_period'] = period_part
                time_part = status_text.split(':', 1)[1]
                time_part = ''.join(c for c in time_part if c.isdigit() or c == ':')
                game_data['time_remaining'] = time_part

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
                            is_winner = spread_value.get('class') and any('__FI-o3p' in c for c in spread_value.get('class', []))
                            game_data['away_spread_winner'] = is_winner
                        if spread_odds:
                            game_data['away_spread_odds'] = spread_odds.text.strip()
                    moneyline_cell = away_cells[2].select_one('span[class*="__p7TUuY"] b')
                    if moneyline_cell:
                        game_data['away_moneyline'] = moneyline_cell.text.strip()
                        is_winner = moneyline_cell.get('class') and any('__FI-o3p' in c for c in moneyline_cell.get('class', []))
                        game_data['away_moneyline_winner'] = is_winner
                    total_cell = away_cells[3].select_one('span[class*="__p7TUuY"]')
                    if total_cell:
                        over_value = total_cell.select_one('b')
                        over_odds = total_cell.find('span')
                        if over_value:
                            game_data['over_value'] = over_value.text.strip().replace('O ', '')
                            is_winner = over_value.get('class') and any('__FI-o3p' in c for c in over_value.get('class', []))
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
                            is_winner = spread_value.get('class') and any('__FI-o3p' in c for c in spread_value.get('class', []))
                            game_data['home_spread_winner'] = is_winner
                        if spread_odds:
                            game_data['home_spread_odds'] = spread_odds.text.strip()
                    moneyline_cell = home_cells[2].select_one('span[class*="__p7TUuY"] b')
                    if moneyline_cell:
                        game_data['home_moneyline'] = moneyline_cell.text.strip()
                        is_winner = moneyline_cell.get('class') and any('__FI-o3p' in c for c in moneyline_cell.get('class', []))
                        game_data['home_moneyline_winner'] = is_winner
                    total_cell = home_cells[3].select_one('span[class*="__p7TUuY"]')
                    if total_cell:
                        under_value = total_cell.select_one('b')
                        under_odds = total_cell.find('span')
                        if under_value:
                            game_data['under_value'] = under_value.text.strip().replace('U ', '')
                            is_winner = under_value.get('class') and any('__FI-o3p' in c for c in under_value.get('class', []))
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

def print_results(parsed_games):
    for i, game in enumerate(parsed_games):
        if not game:
            continue
        print(f"Game {i + 1}:")
        if 'away_team' in game:
            away_record = f" ({game['away_record']})" if 'away_record' in game else ""
            print(f"  Away Team: {game['away_team']} {away_record}")
        if 'home_team' in game:
            home_record = f" ({game['home_record']})" if 'home_record' in game else ""
            print(f"  Home Team: {game['home_team']} {home_record}")
        if 'current_period' in game:
            status = game['current_period']
            if 'time_remaining' in game:
                status += f" {game['time_remaining']}"
            print(f"  Game Status: {status}")
        if 'away_score' in game and 'home_score' in game:
            print(f"  Score: {game['away_team']} {game['away_score']} - {game['home_team']} {game['home_score']}")
        if 'away_moneyline' in game:
            winner = "✓" if game.get('away_moneyline_winner', False) else " "
            print(f"  Away Moneyline: {game['away_moneyline']} {winner}")
        if 'home_moneyline' in game:
            winner = "✓" if game.get('home_moneyline_winner', False) else " "
            print(f"  Home Moneyline: {game['home_moneyline']} {winner}")
        if 'away_spread' in game:
            winner = "✓" if game.get('away_spread_winner', False) else " "
            odds = f" ({game['away_spread_odds']})" if 'away_spread_odds' in game else ""
            print(f"  Away Spread: {game['away_spread']}{odds} {winner}")
        if 'home_spread' in game:
            winner = "✓" if game.get('home_spread_winner', False) else " "
            odds = f" ({game['home_spread_odds']})" if 'home_spread_odds' in game else ""
            print(f"  Home Spread: {game['home_spread']}{odds} {winner}")
        if 'over_value' in game:
            winner = "✓" if game.get('over_winner', False) else " "
            odds = f" ({game['over_odds']})" if 'over_odds' in game else ""
            print(f"  Over: {game['over_value']}{odds} {winner}")
        if 'under_value' in game:
            winner = "✓" if game.get('under_winner', False) else " "
            odds = f" ({game['under_odds']})" if 'under_odds' in game else ""
            print(f"  Under: {game['under_value']}{odds} {winner}")
        print()


print_results(scrape_nhl_odds())
