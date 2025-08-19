# Bet NHL
### By: David Zhong

## Description
Real-time NHL betting program that displays live odds, game statuses, and results in a clean layout. Built for simulated betting and strategy testing, it helps betters make informed predictions.

## Features
- Scrapes today's NHL betting odds using BeautifulSoup via [USAToday](https://sportsdata.usatoday.com/hockey/nhl/odds). I've experimented with other sites, such as CBS Sports, ESPN, Yahoo, etc, but found that USA Today is quite good and the least problematic.
- When there are games today, users will be able to place bets/parlays on spreads, moneylines, and totals. The bets are recorded in a Google Sheet, which I found was the most practical and simple for my everyday use.  

## Technologies
- Python
- HTML/CSS
- JavaScript
- Flask
- BeautifulSoup

## Future Features
- Automatic bet check
