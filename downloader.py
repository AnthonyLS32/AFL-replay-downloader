import argparse
import os
import sys
import requests
from bs4 import BeautifulSoup
import yt_dlp

def parse_duration(text):
    parts = list(map(int, text.split(":")))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        return 0
    return h*3600 + m*60 + s

# --- CLI args ---
parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=100,
                    help="How many latest videos to fetch")
parser.add_argument("--label", type=str, default="latest",
                    help="Filename prefix (e.g. date label)")
args = parser.parse_args()

limit  = args.limit
label  = args.label
DL_DIR = "./AFL_Replays"
os.makedirs(DL_DIR, exist_ok=True)
log_file = os.path.join(DL_DIR, "download_log.txt")

print(f"Label prefix     = {label}")
print(f"Fetch limit      = {limit}")
print(f"Download folder  = {DL_DIR}")

# --- Fetch the latest videos listing ---
listing_url = f"https://www.afl.com.au/video?limit={limit}&sort=latest"
print(f"\n→ GET {listing_url}")
resp = requests.get(listing_url, headers={"User-Agent":"Mozilla/5.0"})
print(f"Status = {resp.status_code}")
if resp.status_code != 200:
    sys.exit("ERROR: Cannot fetch video listing.")

soup = BeautifulSoup(resp.text, "html.parser")

# --- Collect only tiles ≥1 hour ---
candidates = []
for a in soup.select("a[href]"):
    dur_el = a.select_one(".video-item__duration")
    if not dur_el:
        continue
    dur = dur_el.get_text(strip=True)
    secs = parse_duration(dur)
    if secs >= 3600:
        href = a["href"]
        url  = href if href.startswith("http") else "https://www.afl.com.au" + href
        candidates.append((dur, url))

print(f"Found {len(candidates)} videos ≥1 hr out of the top {limit}.")

if not candidates:
    sys.exit("No full-length replays found in the latest videos.")

# --- Download each via yt-dlp ---
ydl_opts = {
    "outtmpl": os.path.join(DL_DIR, f"{label} - %(title)s.%(ext)s"),
    "format":  "bestvideo+bestaudio/best",
    "noprogress": True,
}

for dur, url in candidates:
    print(f"\n→ Downloading ({dur}): {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"ERROR: {e}")

print("\nAll done!")
