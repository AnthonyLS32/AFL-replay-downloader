import argparse
import os
import sys
import datetime
import requests
from bs4 import BeautifulSoup

# Parse --date argument
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="YYYY-MM-DD", required=False)
args = parser.parse_args()
date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

# Paths
DL_PATH = "./AFL_Replays"
LOG_FILE = os.path.join(DL_PATH, "download_log.txt")

# Debug output
print(f"Working dir        = {os.getcwd()}")
print(f"Download folder    = {DL_PATH}")
print(f"Log file           = {LOG_FILE}")
print(f"Downloading date   = {date_str}")

# Ensure download folder exists
if not os.path.isdir(DL_PATH):
    print(f"Creating folder: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

# Fetch match page
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})
matches_url = f"https://www.afl.com.au/matches?date={date_str}"

print(f"Fetching matches page: {matches_url}")
resp = session.get(matches_url)
print(f"Status = {resp.status_code}")

if resp.status_code != 200:
    print("ERROR: Unable to fetch matches page.")
    sys.exit(1)

# Parse replay links
soup = BeautifulSoup(resp.text, "html.parser")
links = [a["href"] for a in soup.select("a.replay-link")]

print(f"Found {len(links)} replay link(s).")
if not links:
    sys.exit(0)

# Load already downloaded log
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(line.strip() for line in f)

# Download loop
with open(LOG_FILE, "a") as log:
    for rel in links:
        name = rel.rsplit("/", 1)[-1] + ".mp4"
        dest = os.path.join(DL_PATH, name)

        if name in downloaded:
            print(f"SKIP {name}")
            continue

        file_url = "https://www.afl.com.au" + rel
        print(f"Downloading {file_url}")
        video_resp = session.get(file_url, stream=True)
        print(f"Status = {video_resp.status_code}")

        if video_resp.status_code != 200:
            print(f"ERROR {name}")
            continue

        with open(dest, "wb") as out:
            for chunk in video_resp.iter_content(1024 * 1024):
                out.write(chunk)

        log.write(name + "\n")
        print(f"DONE {name}")
