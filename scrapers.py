from login import login
import requests
from bs4 import BeautifulSoup

def fetch_upcoming_tournaments(soup):
    upcoming_tournaments = soup.find_all('table', id='upcoming')
    if not upcoming_tournaments:
        print("No upcoming tournaments found")
        return []
    
    print("\n--------- UPCOMING TOURNAMENTS ---------")
    tournaments = []
    for row in upcoming_tournaments:
        tournament_name = row.find('a', class_='plain full marno padvertless hover padleft')
        tournament_date = row.find('td', class_='padleft')
        tournament_event = row.find('a', class_='plain full marno padmore hover')
        tournament_confirmation = row.find('span')
        
        if not (tournament_name and tournament_date and tournament_event and tournament_confirmation):
            print("No upcoming tournaments found")
            return []
        
        tournaments.append({
            'name': tournament_name.text.strip(),
            'date': tournament_date.text.strip(),
            'event': tournament_event.text.strip(),
            'confirmation': tournament_confirmation.text.strip()
        })
        
    return tournaments

def fetch_tournament_history(soup):
    print("\n--------- TOURNAMENT HISTORY  ---------")
    tournament_history = []
    raw_data = []
    history_tournaments = soup.find_all('div', class_='screens results')
    
    if not history_tournaments:
        print("No tournament history found")
        return []
    
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
    if not points_stats:
        print("No NSDA points found")
        return {}
    
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
                data['eligibility'] = "You ARE eligible" in text
    
    return data

def fetch_tournament_signups(soup):
    print("\n--------- TOURNAMENTS TO SIGN UP FOR --------- ")
    tournament_table = soup.find('table', id='signup_table')
    if not tournament_table:
        print("No tournaments to sign up for found")
        return []
    
    signups = []
    for row in tournament_table.find_all('tr', class_='row'):
        tournament_cell = row.find('td', class_='nospace smallish')
        if not tournament_cell:
            continue
        
        name_div = tournament_cell.find('div', class_='nowrap full nospace padvertless')
        location_div = name_div.find_next_sibling('div') if name_div else None
        
        tournament_name = name_div.text.strip() if name_div else ''
        tournament_location = ' '.join(location_div.text.strip().split()) if location_div else ''
        
        date = row.find_all('td', class_='smallish')[1].text.strip() if len(row.find_all('td', class_='smallish')) > 1 else ''
        signup_deadline = row.find_all('td', class_='smallish')[2].text.strip().replace('\n', '').replace('\t', '') if len(row.find_all('td', class_='smallish')) > 2 else ''
        events = row.find('td', class_='nospace centeralign nospace smallish').text.strip() if row.find('td', class_='nospace centeralign nospace smallish') else ''
        info = row.find('td', class_='nospace centeralign nospace smallish').find_next_sibling('td', class_='centeralign').text.strip() if row.find('td', class_='nospace centeralign nospace smallish') and row.find('td', class_='nospace centeralign nospace smallish').find_next_sibling('td', class_='centeralign') else ''
        
        signups.append({
            'name': tournament_name,
            'location': tournament_location,
            'date': date,
            'signup_deadline': signup_deadline,
            'events': events,
            'info': info
        })
    
    return signups

def fetch_paradigm(soup, EMAIL, PASSWORD):
    print("\n--------- JUDGE PARADIGM ---------")
    paradigm_link = soup.find('a', class_='fa fa-lg fa-file-text-o buttonwhite bluetext')
    if not paradigm_link:
        print("No paradigm found")
        return ""
    
    redirect_link = "https://www.tabroom.com" + paradigm_link['href']
    print(f"Accessing paradigm at: {redirect_link}")

    session = requests.Session()
    specific_paradigm = login(redirect_link, EMAIL, PASSWORD, session, nsda=False, paradigm=False, specific_paradigm=True, specific_paradigm_link=redirect_link)
    
    if specific_paradigm is None:
        print("Failed to access paradigm page - login failed")
        return ""
        
    paradigm_soup = BeautifulSoup(specific_paradigm, 'html.parser')
    paradigm_div = paradigm_soup.find('div', class_='paradigm ltborderbottom')
    
    if paradigm_div is None:
        print("Could not find paradigm textarea on page")
        return ""
        
    paradigm_text = ""
    processed_text = set()
    for element in paradigm_div.descendants:
        if element.name == 'li':
            text = element.text.strip()
            if text not in processed_text:
                paradigm_text += "\t– " + text + "\n"
                processed_text.add(text)
        elif isinstance(element, str) and element.strip():
            text = element.strip()
            if text not in processed_text and not any(text in p for p in processed_text):
                paradigm_text += text + "\n"
                processed_text.add(text)
    
    if not paradigm_text:
        print("Found textarea but paradigm text was empty")
        return ""
        
    return paradigm_text.strip()

def fetch_account_info(soup):
    print("\n--------- ACCOUNT INFO ---------")
    account_info = {}

    email = soup.find('input', {'name': 'email'})
    first_name = soup.find('input', {'name': 'first'})
    middle_name = soup.find('input', {'name': 'middle'})
    last_name = soup.find('input', {'name': 'last'})
    phone_number = soup.find('input', {'name': 'phone'})
    pronouns = soup.find('input', {'name': 'pronoun'})
    time_zone = soup.find('select', {'name': 'timezone'}).find('option', selected=True)
    street_address = soup.find('input', {'name': 'street'})
    city = soup.find('input', {'name': 'city'})
    state = soup.find('select', {'name': 'state'}).find('option', selected=True)
    country = soup.find('select', {'name': 'country'}).find('option', selected=True)
    zip_code = soup.find('input', {'name': 'zip'})
    no_email = soup.find('input', {'name': 'no_email'})

    if not (email and first_name and middle_name and last_name and phone_number and pronouns and time_zone and street_address and city and state and country and zip_code and no_email):
        print("No account info found")
        return {}

    account_info['email'] = email['value']
    account_info['first_name'] = first_name['value']
    account_info['middle_name'] = middle_name['value']
    account_info['last_name'] = last_name['value']
    account_info['phone_number'] = phone_number['value']
    account_info['pronouns'] = pronouns['value']
    account_info['time_zone'] = time_zone['value']
    account_info['street_address'] = street_address['value']
    account_info['city'] = city['value']
    account_info['state'] = state['value']
    account_info['country'] = country['value']
    account_info['zip_code'] = zip_code['value']
    account_info['no_email'] = no_email['value']

    return account_info
