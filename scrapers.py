def fetch_upcoming_tournaments(soup):
    upcoming_tournaments = soup.find_all('table', id='upcoming')
    print("\n--------- UPCOMING TOURNAMENTS ---------")
    for row in upcoming_tournaments:
        tournaments = []
        
        tournament_name = row.find('a', class_='plain full marno padvertless hover padleft').text.strip()
        tournament_date = row.find('td', class_='padleft').text.strip()
        tournament_event = row.find('a', class_='plain full marno padmore hover').text.strip()
        tournament_confirmation = row.find('span').text.strip()
        
        tournaments.append({'name': tournament_name, 'date': tournament_date, 'event': tournament_event, 'confirmation': tournament_confirmation})
        
        return tournaments
    
def fetch_tournament_history(soup):
    print("\n--------- TOURNAMENT HISTORY  ---------")
    tournament_history = []
    raw_data = []
    history_tournaments = soup.find_all('div', class_='screens results')
    
    for table in history_tournaments:
        for row in table.find_all('tr'):
            for cell in row.find_all('td'):
                raw_data.append(cell.text.strip())
    
    for i in range(0, len(raw_data), 5):
        tournament_history.append({'name': raw_data[i], 'date': raw_data[i + 1], 'code': raw_data[i + 2], 'event': raw_data[i + 3]})
    
    return tournament_history

def fetch_nsda_points(soup):
    print("\n--------- NSDA POINTS ---------")
    points_stats = soup.find_all('span', class_='threefifths leftalign semibold')
    final_text = ""
    
    data = {'degree': '', 'current_points': 0, 'to_next_degree': 0, 'last_posted': '', 'eligibility': False }

    for stat in points_stats:
        for div in stat.find_all('div'):
            text = div.text.strip()
            text = ' '.join(text.split())
            if 'Degree of' in text:
                degree_index = text.find("Degree of ")
                data['degree'] = text[degree_index + 10:]
            if 'merit points' in text:
                bar_index = text.find(" | ")
                merit_index = text.find(" merit points")
                next_index = text.find(" to next degree")
                data['current_points'] = int(text[:merit_index])
                data['to_next_degree'] = int(text[bar_index + 3:next_index])
            if 'Last points posted' in text:
                last_index = text.find("posted on ")
                data['last_posted'] = text[last_index + 10:]
            if 'to enter the' in text:
                if "You ARE eligible" in text:
                    data['eligibility'] = True
                else:
                    data['elibigility'] = False
    
    return data


# TODO: FIX THE SCRAPER DATA ISSUES
def fetch_tournament_signups(soup):
    print("\n--------- TOURNAMENTS TO SIGN UP FOR --------- ")
    tournament_table = soup.find('table', id='signup_table')
    signups = []
    
    for body in tournament_table.find_all('tbody'):
        for tournament in body.find_all("tr"):
            tournament_name = tournament.select_one('td', class_='nospace smallish').text.strip()
            tournament_name = ' '.join(tournament_name.split())
            tournament_date = tournament.find('td', class_='smallish').text.strip()
            tournament_date = ' '.join(tournament_date.split())
            tournament_events = tournament.find('td', class_='nospace centeralign nospace smallish').text.strip()
            tournament_events = ' '.join(tournament_events.split())
            tournament_info = tournament.find('td', class_='centeralign').text.strip()
            tournament_info = ' '.join(tournament_info.split())

            signups.append({'name': tournament_name, 'date': tournament_date, 'events': tournament_events, 'info': tournament_info})
        
    return signups
