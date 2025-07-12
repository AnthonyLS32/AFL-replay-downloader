import argparse
import os
import sys
import datetime
import requests
from bs4 import BeautifulSoup

# --- Args & Paths ---
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="YYYY-MM-DD", required=False)
args = parser.parse_args()
date_str = args.date or datetime.date.today().strftime("%Y-%m-%d")

DL_PATH  = "./AFL_Replays"
LOG_FILE = os.path.join(DL_PATH, "download_log.txt")
BASE_URL = "https://www.afl.com.au"

# --- Prep ---
print(f"Working dir      = {os.getcwd()}")
print(f"Download folder  = {DL_PATH}")
print(f"Log file         = {LOG_FILE}")
print(f"Downloading date = {date_str}")

if not os.path.isdir(DL_PATH):
    print(f"Creating folder: {DL_PATH}")
    os.makedirs(DL_PATH, exist_ok=True)

session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

# --- Step 1: Fetch matches page & collect any .mp4 links ---
matches_url = f"{BASE_URL}/matches?date={date_str}"
print(f"\n→ GET {matches_url}")
resp = session.get(matches_url)
print(f"Status = {resp.status_code}")

soup = BeautifulSoup(resp.text, "html.parser")

# direct mp4s
links = set()
for a in soup.find_all("a", href=True):
    href = a["href"]
    if href.lower().endswith(".mp4"):
        full = href if href.startswith("http") else BASE_URL + href
        links.add(full)

print(f"Direct .mp4 links found on matches page: {len(links)}")

# --- Step 2: If none, crawl into each match-centre link ---
if not links:
    match_pages = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/match-centre/" in href:
            full = href if href.startswith("http") else BASE_URL + href
            match_pages.add(full)
    print(f"Found {len(match_pages)} match-centre page link(s).")

    for mp in match_pages:
        print(f"\n→ GET {mp}")
        mresp = session.get(mp)
        print(f"Status = {mresp.status_code}")
        msoup = BeautifulSoup(mresp.text, "html.parser")
        for a2 in msoup.find_all("a", href=True):
            href2 = a2["href"]
            if href2.lower().endswith(".mp4"):
                full2 = href2 if href2.startswith("http") else BASE_URL + href2
                links.add(full2)
    print(f"Total .mp4 links after crawling each match page: {len(links)}")

if not links:
    print("No .mp4 links found. Check that AFL has published On-Demand replays for this date.")
    sys.exit(0)

# --- Step 3: Download each unique link, skipping already-downloaded ---
downloaded = set()
if os.path.isfile(LOG_FILE):
    with open(LOG_FILE) as f:
        downloaded = set(l.strip() for l in f)

with open(LOG_FILE, "a") as log:
    for url in sorted(links):
        fname = url.rsplit("/", 1)[-1]
        dest  = os.path.join(DL_PATH, fname)
        if fname in downloaded or os.path.isfile(dest):
            print(f"SKIP {fname}")
            continue

        print(f"\nDOWNLOAD → {url}")
        r = session.get(url, stream=True)
        print(f"Status = {r.status_code}")
        if r.status_code != 200:
            print(f"ERROR downloading {fname}")
            continue

        with open(dest, "wb") as out:
            for chunk in r.iter_content(1024*1024):
                out.write(chunk)

        log.write(fname + "\n")
        print(f"DONE {fname}")
