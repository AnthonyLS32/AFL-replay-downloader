import argparse
import datetime
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import yt_dlp

# 1. CLI args
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="YYYY-MM-DD (defaults today)", required=False)
args = parser.parse_args()

target_date = (
    args.date
    or datetime.date.today().strftime("%Y-%m-%d")
)
print(f"Target date = {target_date}")

# 2. Prepare download folder
DL_PATH = "./AFL_Replays"
os.makedirs(DL_PATH, exist_ok=True)
print(f"Download folder = {DL_PATH}")

# 3. Fetch the Match Replays listing
LISTING_URL = (
    "https://www.afl.com.au/video?"
    "tagNames=ProgramCategory%3AMatch%20Replays&limit=100"
)
print(f"\n→ GET {LISTING_URL}")
resp = requests.get(LISTING_URL, headers={"User-Agent":"Mozilla/5.0"})
print(f"Status = {resp.status_code}")
if resp.status_code != 200:
    sys.exit("Failed to fetch Match Replays listing.")

soup = BeautifulSoup(resp.text, "html.parser")

# 4. Extract replay links + publishFrom timestamp
pattern = re.compile(r"/video/\d+/match-replay-[^?]+\?.*publishFrom=(\d+)")
candidates = []
for a in soup.find_all("a", href=True):
    m = pattern.search(a["href"])
    if not m:
        continue
    ts_ms = int(m.group(1))
    dt = datetime.datetime.utcfromtimestamp(ts_ms/1000).date()
    url = a["href"]
    full_url = url if url.startswith("http") else "https://www.afl.com.au" + url
    candidates.append((dt.strftime("%Y-%m-%d"), full_url))

print(f"Found {len(candidates)} replay tiles in listing.")

# 5. Filter by your date
links = [url for (d, url) in candidates if d == target_date]
print(f"Matched {len(links)} replays on {target_date}.")

if not links:
    sys.exit("No replays found for that date or not published yet.")

# 6. Download with yt-dlp
ydl_opts = {
    "outtmpl": os.path.join(DL_PATH, "%(title)s.%(ext)s"),
    "format":  "bestvideo+bestaudio/best",
    "noprogress": True
}

for url in sorted(links):
    print(f"\n→ yt-dlp downloading: {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"ERROR downloading {url}: {e}")

print("\nAll done!")
