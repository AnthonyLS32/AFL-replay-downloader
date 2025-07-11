import requests
import os
import configparser
import datetime
from bs4 import BeautifulSoup
import keyring

# Load config
cfg = configparser.ConfigParser()
cfg.read('config.ini')
USER = cfg['afl']['username']
PW_KEY = cfg['afl']['password_key']
DOWNLOAD_FOLDER = cfg['paths']['download_folder']
LOG_FILE = cfg['paths']['log_file']

# Retrieve password
password = keyring.get_password(PW_KEY, "user")

session = requests.Session()
# Perform login (adjust endpoints and tokens as needed)
session.get("https://www.afl.com.au/login")
payload = {"username": USER, "password": password}
session.post("https://www.afl.com.au/login/authenticate", data=payload)

# Scrape for replay links
today = datetime.date.today().strftime("%Y-%m-%d")
replays_page = session.get(f"https://www.afl.com.au/matches?date={today}")
soup = BeautifulSoup(replays_page.text, "html.parser")
links = [a['href'] for a in soup.select("a.replay-link")]

# Ensure download folder exists
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Load already downloaded
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(line.strip() for line in f)

with open(LOG_FILE, "a") as log:
    for rel in links:
        url = f"https://www.afl.com.au{rel}"
        filename = rel.split("/")[-1] + ".mp4"
        dest = os.path.join(DOWNLOAD_FOLDER, filename)
        if filename in downloaded:
            continue
        r = session.get(url, stream=True)
        with open(dest, "wb") as out:
            for chunk in r.iter_content(1024*1024):
                out.write(chunk)
        log.write(filename + "\n")
        print(f"Downloaded {filename}")
