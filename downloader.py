import requests
import os
import configparser
import datetime
import keyring
from bs4 import BeautifulSoup

# Load config
cfg = configparser.ConfigParser()
cfg.read('config.ini')

USER     = cfg['afl']['username']
PW_KEY   = cfg['afl']['password_key']
DL_PATH  = cfg['paths']['download_folder']
LOG_FILE = cfg['paths']['log_file']

# Debug prints to verify paths and working dir
print(f"[DEBUG] AFL user        = {USER}")
print(f"[DEBUG] Download folder = {DL_PATH!r}")
print(f"[DEBUG] Log file path   = {LOG_FILE!r}")
print(f"[DEBUG] CWD             = {os.getcwd()}")
print(f"[DEBUG] Path exists?    = {os.path.isdir(DL_PATH)}")

# Ensure download folder exists
if not os.path.isdir(DL_PATH):
    print(f"[DEBUG] Creating download dir: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

# Retrieve password
password = keyring.get_password(PW_KEY, 'user')
if not password:
    raise RuntimeError("No password found in keyring. Run credential_manager.py first.")
print("[DEBUG] Retrieved password from keyring")

# Start session and login
session = requests.Session()
login_page = session.get("https://www.afl.com.au/login")
print(f"[DEBUG] Login page status       = {login_page.status_code}")

payload = {"username": USER, "password": password}
resp = session.post("https://www.afl.com.au/login/authenticate", data=payload)
print(f"[DEBUG] Auth response status    = {resp.status_code}")

# Scrape for replay links
today_str  = datetime.date.today().strftime("%Y-%m-%d")
matches_url = f"https://www.afl.com.au/matches?date={today_str}"
print(f"[DEBUG] Scraping replays from   = {matches_url}")

replays_page = session.get(matches_url)
print(f"[DEBUG] Replays page status     = {replays_page.status_code}")

soup  = BeautifulSoup(replays_page.text, "html.parser")
links = [a['href'] for a in soup.select("a.replay-link")]

if not links:
    print("[WARN] No replay links found. Check your CSS selector or page markup.")
    exit()

print(f"[DEBUG] Found {len(links)} replay link(s):")
for link in links:
    print("  ", link)

# Load already downloaded filenames
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(line.strip() for line in f)

# Download loop
with open(LOG_FILE, "a") as log:
    for rel in links:
        filename = rel.split("/")[-1] + ".mp4"
        dest     = os.path.join(DL_PATH, filename)

        if filename in downloaded:
            print(f"[SKIP] {filename} already downloaded.")
            continue

        file_url = f"https://www.afl.com.au{rel}"
        print(f"[DOWNLOAD] Fetching {file_url}")
        r = session.get(file_url, stream=True)
        print(f"[DEBUG] Stream status          = {r.status_code}")

        if r.status_code != 200:
            print(f"[ERROR] Failed to download {filename}")
            continue

        with open(dest, "wb") as out_file:
            for chunk in r.iter_content(1024 * 1024):
                out_file.write(chunk)

        log.write(filename + "\n")
        print(f"[DONE] Downloaded {filename}")
