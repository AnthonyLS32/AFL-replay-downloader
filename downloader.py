import argparse
import requests
import os
import configparser
import datetime
import keyring
from bs4 import BeautifulSoup

# --- CLI args ---
parser = argparse.ArgumentParser()
parser.add_argument(
    "--date",
    help="Date to download replays (YYYY-MM-DD). Defaults to today.",
    required=False,
)
args = parser.parse_args()

# pick date
if args.date:
    date_str = args.date
else:
    date_str = datetime.date.today().strftime("%Y-%m-%d")

# --- Load config ---
cfg = configparser.ConfigParser()
cfg.read('config.ini')

USER     = cfg['afl']['username']
PW_KEY   = cfg['afl']['password_key']
DL_PATH  = cfg['paths']['download_folder']
LOG_FILE = cfg['paths']['log_file']

print(f"[DEBUG] User         = {USER}")
print(f"[DEBUG] Date         = {date_str}")
print(f"[DEBUG] Download dir = {DL_PATH!r}")
print(f"[DEBUG] Log file     = {LOG_FILE!r}")
print(f"[DEBUG] CWD          = {os.getcwd()}")

# ensure folder exists
if not os.path.isdir(DL_PATH):
    print(f"[DEBUG] Creating folder: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

# retrieve password
password = keyring.get_password(PW_KEY, 'user')
if not password:
    raise RuntimeError("Password not found in keyring. Run credential_manager.py first.")
print("[DEBUG] Retrieved password from keyring")

# login
session = requests.Session()
print("[DEBUG] Fetching login page…")
lp = session.get("https://www.afl.com.au/login")
print(f"[DEBUG] Login page status = {lp.status_code}")

payload = {"username": USER, "password": password}
auth = session.post("https://www.afl.com.au/login/authenticate", data=payload)
print(f"[DEBUG] Auth response status = {auth.status_code}")

# scrape
matches_url = f"https://www.afl.com.au/matches?date={date_str}"
print(f"[DEBUG] Scraping: {matches_url}")
r = session.get(matches_url)
print(f"[DEBUG] Page status = {r.status_code}")

soup = BeautifulSoup(r.text, "html.parser")
links = [a['href'] for a in soup.select("a.replay-link")]

if not links:
    print("[WARN] No replay links found. Check the date or selector.")
    exit()

print(f"[DEBUG] Found {len(links)} replay link(s).")

# load downloaded log
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(l.strip() for l in f)

# download each
with open(LOG_FILE, "a") as log:
    for rel in links:
        fname = rel.split("/")[-1] + ".mp4"
        dest  = os.path.join(DL_PATH, fname)

        if fname in downloaded:
            print(f"[SKIP] {fname} already downloaded.")
            continue

        file_url = f"https://www.afl.com.au{rel}"
        print(f"[DOWNLOAD] {file_url}")
        stream = session.get(file_url, stream=True)
        print(f"[DEBUG] Stream status = {stream.status_code}")

        if stream.status_code != 200:
            print(f"[ERROR] Failed to download {fname}")
            continue

        with open(dest, "wb") as f_out:
            for chunk in stream.iter_content(1024*1024):
                f_out.write(chunk)

        log.write(fname + "\n")
        print(f"[DONE] Downloaded {fname}")
