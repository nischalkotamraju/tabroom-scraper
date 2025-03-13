#TODO Add checks for if page was logged into correctly
import os
import requests
from bs4 import BeautifulSoup
import sys

def login(loginPageURL, EMAIL: str, PASSWORD: str, session, nsda: bool):
    try:
        session = requests.Session()
        
        try:
            loginPageData = session.get(loginPageURL)
            loginPageData.raise_for_status()  # Check if the request was successful
        except requests.RequestException as e:
            raise Exception(f"Failed to access login page: {e}")

        try:
            loginSoup = BeautifulSoup(loginPageData.content, "html.parser")
        except Exception as e:
            raise Exception(f"Failed to parse login page: {e}")
        except TypeError as e:
            raise Exception(f"Failed to parse login page: {e}")

        # Get SHA value
        try:
            shaVal = loginSoup.find("input", attrs={"name":"sha"})['value']
        except (AttributeError, KeyError, TypeError):
            raise Exception("SHA value not found in the login page")

        # Get Salt value
        try:
            saltVal = loginSoup.find("input", attrs={"name":"salt"})['value']
        except (AttributeError, KeyError, TypeError):
            raise Exception("Salt value not found in the login page")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
        }

        data = {
            'salt': saltVal,
            'sha': shaVal,
            'username': EMAIL,
            'password': PASSWORD,
        }

        try:
            login_response = session.post('https://www.tabroom.com/user/login/login_save.mhtml', 
                                       headers=headers, 
                                       data=data)
            login_response.raise_for_status()
        except requests.RequestException as e:
            raise Exception(f"Login request failed: {e}")

        try:
            if (nsda):
                dashboard = session.get("https://www.tabroom.com/user/student/nsda.mhtml")
            else:
                dashboard = session.get("https://www.tabroom.com/user/student/")
            
            dashboard.raise_for_status()
            return dashboard.content
        except requests.RequestException as e:
            raise Exception(f"Failed to access dashboard: {e}")

    except Exception as e:
        print(f"Login failed: {e}")
        return None


def get_password(prompt="Enter your Tabroom password: "):
    password = ""
    print(prompt, end='', flush=True)
    
    while True:
        try:
            import tty
            import termios
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(sys.stdin.fileno())
                char = sys.stdin.read(1)
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        
            if char == '\r' or char == '\n':
                print()
                break
            elif char == '\b' or char == '\x7f':
                if len(password) > 0:
                    password = password[:-1]
                    print('\b \b', end='', flush=True)
            else:
                password += char
                print('*', end='', flush=True)
        except UnicodeDecodeError:
            continue
            
    return password