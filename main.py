from bs4 import BeautifulSoup
from login import login, get_password
import requests
from scrapers import fetch_upcoming_tournaments, fetch_tournament_history, fetch_nsda_points, fetch_tournament_signups
import os

def clear_console():
    os.system('clear' if os.name == 'posix' else 'cls')

'''
EMAIL = input("Enter your Tabroom email: ")
PASSWORD = get_password()
'''

EMAIL = "kotamrajunischal101@gmail.com"
PASSWORD = "Nischal101!"

session = requests.Session()
dashboard_content = login('https://www.tabroom.com/user/login/login.mhtml', EMAIL, PASSWORD, session, nsda=False)
dashboard_soup = BeautifulSoup(dashboard_content, 'html.parser')
clear_console()

for upcoming_tournament in fetch_upcoming_tournaments(dashboard_soup):
    print(upcoming_tournament)

for past_tournament in fetch_tournament_history(dashboard_soup):
    print(past_tournament)

for signup in fetch_tournament_signups(dashboard_soup):
    print(signup)

nsda_content = login('https://www.tabroom.com/user/login/login.mhtml', EMAIL, PASSWORD, session, nsda=True)
nsda_soup = BeautifulSoup(nsda_content, 'html.parser')
print(fetch_nsda_points(nsda_soup))