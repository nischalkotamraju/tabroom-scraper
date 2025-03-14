from login import login
import requests
from bs4 import BeautifulSoup

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
                    data['eligibility'] = False
    
    return data


# TODO: FIX THE SCRAPER DATA ISSUES
def fetch_tournament_signups(soup):
    print("\n--------- TOURNAMENTS TO SIGN UP FOR --------- ")
    tournament_table = soup.find('table', id='signup_table')
    signups = []
    
    if tournament_table:
        for row in tournament_table.find_all('tr', class_='row'):
            tournament_cell = row.find('td', class_='nospace smallish')
            name_div = tournament_cell.find('div', class_='nowrap full nospace padvertless')
            location_div = name_div.find_next_sibling('div')
            
            tournament_name = name_div.text.strip()
            # Add space before state/location code
            tournament_location = ' '.join(location_div.text.strip().split()) if location_div else ''
            
            date = row.find_all('td', class_='smallish')[1].text.strip()
            signup_deadline = row.find_all('td', class_='smallish')[2].text.strip().replace('\n', '').replace('\t', '')
            events = row.find('td', class_='nospace centeralign nospace smallish').text.strip()
            info = row.find('td', class_='nospace centeralign nospace smallish').find_next_sibling('td', class_='centeralign').text.strip()
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
    redirect_link = ""
    
    if paradigm_link:
        redirect_link = "https://www.tabroom.com" + paradigm_link['href']
        print(f"Accessing paradigm at: {redirect_link}")

        session = requests.Session()
        specific_paradigm = login(redirect_link, EMAIL, PASSWORD, session, nsda=False, paradigm=False, specific_paradigm=True, specific_paradigm_link=redirect_link)
        
        if specific_paradigm is None:
            print("Failed to access paradigm page - login failed")
            return "No paradigm found - login failed"
            
        paradigm_soup = BeautifulSoup(specific_paradigm, 'html.parser')
        paradigm_div = paradigm_soup.find('div', class_='paradigm ltborderbottom')
        
        if paradigm_div is None:
            print("Could not find paradigm textarea on page")
            return "No paradigm found - textarea not found"
            
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
            return "No paradigm found - empty"
            
        return paradigm_text.strip()
    
def fetch_account_info(soup):
    print("\n--------- ACCOUNT INFO ---------")
    account_info = {}

    account_info['email'] = soup.find('input', {'name': 'email'})['value']
    account_info['first_name'] = soup.find('input', {'name': 'first'})['value']
    account_info['middle_name'] = soup.find('input', {'name': 'middle'})['value']
    account_info['last_name'] = soup.find('input', {'name': 'last'})['value']
    account_info['phone_number'] = soup.find('input', {'name': 'phone'})['value']
    account_info['pronouns'] = soup.find('input', {'name': 'pronoun'})['value']
    account_info['time_zone'] = soup.find('select', {'name': 'timezone'}).find('option', selected=True)['value']
    account_info['street_address'] = soup.find('input', {'name': 'street'})['value']
    account_info['city'] = soup.find('input', {'name': 'city'})['value']
    account_info['state'] = soup.find('select', {'name': 'state'}).find('option', selected=True)['value']
    account_info['country'] = soup.find('select', {'name': 'country'}).find('option', selected=True)['value']
    account_info['zip_code'] = soup.find('input', {'name': 'zip'})['value']
    account_info['no_email'] = soup.find('input', {'name': 'no_email'})['value']

    return account_info

