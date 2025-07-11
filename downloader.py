import argparse
import os
import configparser
import datetime
import sys
import requests
from bs4 import BeautifulSoup

# CLI args
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="YYYY-MM-DD", required=False)
args = parser.parse_args()
date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

# Load config
cfg = configparser.ConfigParser()
cfg.read('config.ini')
DL_PATH  = cfg['paths']['download_folder']
LOG_FILE = cfg['paths']['log_file']
USER     = cfg['afl']['username']
PASSWORD = cfg['afl'].get('password') or None

# Debug info
print(f"Working dir        = {os.getcwd()}")
print(f"Download folder    = {DL_PATH}")
print(f"Log file           = {LOG_FILE}")
print(f"Downloading date   = {date_str}")

# Ensure download folder exists
if not os.path.isdir(DL_PATH):
    print(f"Creating folder: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

# Login
session = requests.Session()
print("Logging in…")
auth = session.post(
    "https://www.afl.com.au/login/authenticate",
    data={"username": USER, "password": PASSWORD}
)
print(f"Login response     = {auth.status_code}")

# Scrape replay links
matches_url = f"https://www.afl.com.au/matches?date={date_str}"
print(f"Scraping URL        = {matches_url}")
r = session.get(matches_url)
print(f"Page status         = {r.status_code}")

soup = BeautifulSoup(r.text, "html.parser")
links = [a['href'] for a in soup.select("a.replay-link")]

if not links:
    print("No replay links found.")
    sys.exit(0)

print(f"Found {len(links)} link(s).")

# Load download log
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(l.strip() for l in f)

# Download loop
with open(LOG_FILE, "a") as log:
    for rel in links:
        name = rel.rsplit("/", 1)[-1] + ".mp4"
        dest = os.path.join(DL_PATH, name)

        if name in downloaded:
            print(f"SKIP   {name}")
            continue

        file_url = f"https://www.afl.com.au{rel}"
        print(f"Downloading → {file_url}")
        stream = session.get(file_url, stream=True)
        print(f"Status      = {stream.status_code}")

        if stream.status_code != 200:
            print(f"ERROR       Failed {name}")
            continue

        with open(dest, "wb") as out:
            for chunk in stream.iter_content(1024*1024):
                out.write(chunk)

        log.write(name + "\n")
        print(f"DONE        {name}")
