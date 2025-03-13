def fetch_upcoming_tournaments(soup):
    upcoming_tournaments = soup.find_all('table', id='upcoming')
    print("\n--------- UPCOMING TOURNAMENTS ---------")
    for row in upcoming_tournaments:
        tournaments = []
        
        tournament_name = row.find('a', class_='plain full marno padvertless hover padleft').text.strip()
        tournament_date = row.find('td', class_='padleft').text.strip()
        tournament_event = row.find('a', class_='plain full marno padmore hover').text.strip()
        tournament_confirmation = row.find('span').text.strip()
        
        tournaments.append(tournament_name + " | " + tournament_date + " | " + tournament_event + " | " + tournament_confirmation)
        
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
        group = raw_data[i:i+4]
        if len(group) == 4:
            tournament_history.append(" | ".join(group))
    
    return tournament_history

def fetch_nsda_points(soup):
    print("\n--------- NSDA POINTS ---------")
    points_stats = soup.find_all('span', class_='threefifths leftalign semibold')
    final_text = ""
    
    for stat in points_stats:
        for div in stat.find_all('div'):
            text = div.text.strip()
            text = ' '.join(text.split())
            final_text += text + "\n"
    
    return final_text