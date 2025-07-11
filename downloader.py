import argparse
import configparser
import datetime
import os
import sys
import requests
from bs4 import BeautifulSoup

# --- CLI args ---
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="YYYY-MM-DD", required=False)
args = parser.parse_args()
date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

# --- Load config ---
cfg = configparser.ConfigParser()
cfg.read('config.ini')
USER     = cfg['afl']['username']
PASSWORD = cfg['afl'].get('password')
DL_PATH  = cfg['paths']['download_folder']
LOG_FILE = cfg['paths']['log_file']

print(f"Working dir      = {os.getcwd()}")
print(f"Download folder  = {DL_PATH}")
print(f"Log file         = {LOG_FILE}")
print(f"Downloading date = {date_str}")

# --- Prep session with browser‐like headers ---
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
})

# --- Ensure download folder exists ---
if not os.path.isdir(DL_PATH):
    print(f"Creating folder: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

# --- Step 1: GET the login page to grab form + hidden fields ---
login_url = "https://www.afl.com.au/login"
print(f"\n→ GET {login_url}")
resp = session.get(login_url)
print(f"Login page status = {resp.status_code}")

soup = BeautifulSoup(resp.text, "html.parser")
form = soup.find("form")
if not form:
    print("ERROR: No <form> found on login page.")
    sys.exit(1)

action = form.get("action", "")
if action.startswith("/"):
    action_url = "https://www.afl.com.au" + action
else:
    action_url = action
print(f"Form action URL   = {action_url}")

# Build payload from all inputs
payload = {}
for inp in form.find_all("input"):
    name = inp.get("name")
    if not name:
        continue
    payload[name] = inp.get("value", "")
# Overwrite with our credentials
payload["username"] = USER
payload["password"] = PASSWORD
print(f"Payload keys      = {list(payload.keys())}")

# --- Step 2: POST login ---
print(f"\n→ POST {action_url}")
login_resp = session.post(action_url, data=payload, headers={"Referer": login_url})
print(f"Login POST status = {login_resp.status_code}")
print(f"Login redirected?  = {login_resp.is_redirect}")

# If 403 persists, dump a snippet of the response
if login_resp.status_code == 403:
    print("\n!!! 403 Forbidden on login. Dumping first 500 chars of response for clues:\n")
    print(login_resp.text[:500])
    sys.exit(1)

# --- Step 3: Scrape for replay links ---
matches_url = f"https://www.afl.com.au/matches?date={date_str}"
print(f"\n→ GET {matches_url}")
match_resp = session.get(matches_url)
print(f"Matches page status = {match_resp.status_code}")

soup = BeautifulSoup(match_resp.text, "html.parser")
links = [a["href"] for a in soup.select("a.replay-link")]
print(f"Found {len(links)} replay link(s).")

if not links:
    print("No replay links found. Check selector or authentication.")
    sys.exit(0)

# --- Step 4: Download loop ---
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(l.strip() for l in f)

with open(LOG_FILE, "a") as log:
    for rel in links:
        name = rel.rsplit("/",1)[-1] + ".mp4"
        dest = os.path.join(DL_PATH, name)

        if name in downloaded:
            print(f"SKIP   {name}")
            continue

        file_url = "https://www.afl.com.au" + rel
        print(f"\nDownloading → {file_url}")
        video_resp = session.get(file_url, stream=True)
        print(f"Video status      = {video_resp.status_code}")

        if video_resp.status_code != 200:
            print(f"ERROR    Failed to download {name}")
            continue

        with open(dest, "wb") as out:
            for chunk in video_resp.iter_content(1024*1024):
                out.write(chunk)

        log.write(name + "\n")
        print(f"DONE     {name}")
