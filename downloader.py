import argparse
import requests
import os
import configparser
import datetime
import keyring
from bs4 import BeautifulSoup

# CLI args
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="YYYY-MM-DD", required=False)
args = parser.parse_args()
date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

# Load config
cfg = configparser.ConfigParser()
cfg.read('config.ini')

USER     = cfg['afl']['username']
PASSWORD = cfg['afl'].get('password') or keyring.get_password(cfg['afl']['password_key'], 'user')
DL_PATH  = cfg['paths']['download_folder']
LOG_FILE = cfg['paths']['log_file']

print(f"[DEBUG] User         = {USER}")
print(f"[DEBUG] Date         = {date_str}")
print(f"[DEBUG] Download dir = {DL_PATH!r}")
print(f"[DEBUG] Log file     = {LOG_FILE!r}")
print(f"[DEBUG] CWD          = {os.getcwd()}")

# Ensure folder exists
if not os.path.isdir(DL_PATH):
    print(f"[DEBUG] Creating folder: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

# Verify password
if not PASSWORD:
    raise RuntimeError("No password found. Add 'password' in config.ini or use keyring.")

# Login
session = requests.Session()
session.get("https://www.afl.com.au/login")
session.post("https://www.afl.com.au/login/authenticate", data={"username": USER, "password": PASSWORD})
print("[DEBUG] Logged in")

# Scrape replay links
matches_url = f"https://www.afl.com.au/matches?date={date_str}"
print(f"[DEBUG] Scraping: {matches_url}")
r = session.get(matches_url)
links = [a['href'] for a in BeautifulSoup(r.text, "html.parser").select("a.replay-link")]

if not links:
    print("[WARN] No replay links found.")
    exit()

# Load download log
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(l.strip() for l in f)

# Download loop
with open(LOG_FILE, "a") as log:
    for rel in links:
        fname = rel.split("/")[-1] + ".mp4"
        dest  = os.path.join(DL_PATH, fname)
        if fname in downloaded:
            print(f"[SKIP] {fname}")
            continue

        file_url = f"https://www.afl.com.au{rel}"
        print(f"[DOWNLOAD] {file_url}")
        stream = session.get(file_url, stream=True)
        if stream.status_code != 200:
            print(f"[ERROR] Failed {fname}")
            continue

        with open(dest, "wb") as f_out:
            for chunk in stream.iter_content(1024*1024):
                f_out.write(chunk)
        log.write(fname + "\n")
        print(f"[DONE] {fname}")
