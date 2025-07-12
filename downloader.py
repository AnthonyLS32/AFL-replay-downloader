import argparse
import datetime
import os
import sys
import requests
from bs4 import BeautifulSoup
import yt_dlp

def parse_duration(text):
    """Convert 'HH:MM:SS' or 'MM:SS' → seconds."""
    parts = list(map(int, text.split(":")))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        return 0
    return h * 3600 + m * 60 + s

# CLI args
parser = argparse.ArgumentParser()
parser.add_argument("--date", help="Label date (YYYY-MM-DD)", required=False)
parser.add_argument("--limit", type=int, default=100, help="How many videos to fetch")
args = parser.parse_args()

label_date = args.date or datetime.date.today().strftime("%Y-%m-%d")
limit      = args.limit

# Prepare download folder
DL_PATH = "./AFL_Replays"
os.makedirs(DL_PATH, exist_ok=True)
log_file = os.path.join(DL_PATH, "download_log.txt")

print(f"Label date       = {label_date}")
print(f"Fetch limit      = {limit}")
print(f"Download folder  = {DL_PATH}")

# Fetch latest videos listing
listing_url = f"https://www.afl.com.au/video?limit={limit}"
print(f"\n→ GET {listing_url}")
resp = requests.get(listing_url, headers={"User-Agent":"Mozilla/5.0"})
print(f"Status = {resp.status_code}")
if resp.status_code != 200:
    sys.exit("ERROR: Cannot fetch video listing.")

soup = BeautifulSoup(resp.text, "html.parser")

# Collect tiles with duration ≥1 hour
candidates = []
for tile in soup.select("a[href]"):
    dur_el = tile.select_one(".video-item__duration")
    if not dur_el:
        continue
    dur_text = dur_el.get_text(strip=True)
    secs = parse_duration(dur_text)
    if secs >= 3600:
        href = tile["href"]
        full_url = href if href.startswith("http") else "https://www.afl.com.au" + href
        candidates.append((dur_text, full_url))

print(f"Found {len(candidates)} videos ≥ 1 hour out of {limit} items.")

if not candidates:
    sys.exit("No replays ≥ 1 hour found.")

# Download each via yt-dlp
ydl_opts = {
    "outtmpl": os.path.join(DL_PATH, f"{label_date} - %(title)s.%(ext)s"),
    "format":  "bestvideo+bestaudio/best",
    "noprogress": True,
}

for dur_text, url in candidates:
    print(f"\n→ yt-dlp downloading ({dur_text}): {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"ERROR downloading {url}: {e}")

print("\nAll done!")
