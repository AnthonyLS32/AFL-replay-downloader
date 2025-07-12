# downloader.py

import argparse
import datetime
import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
import yt_dlp

def parse_duration(text):
    """Convert 'HH:MM:SS' or 'MM:SS' → total seconds."""
    parts = list(map(int, text.split(":")))
    if len(parts) == 3:
        h, m, s = parts
    elif len(parts) == 2:
        h, m, s = 0, parts[0], parts[1]
    else:
        return 0
    return h*3600 + m*60 + s

# --- CLI args ---
p = argparse.ArgumentParser()
p.add_argument("--limit", type=int, default=100,
               help="How many videos the listing page should request")
p.add_argument("--label", type=str, default="latest",
               help="Filename prefix (e.g. date label)")
args = p.parse_args()

limit = args.limit
label = args.label
DL_DIR = "./AFL_Replays"
os.makedirs(DL_DIR, exist_ok=True)

print(f"Fetch limit      = {limit}")
print(f"Filename prefix  = {label}")
print(f"Download folder  = {DL_DIR}")

# --- Step 1: Fetch the SSR page with Apollo state ---
LISTING_URL = (
    "https://www.afl.com.au/video?"
    "tagNames=ProgramCategory%3AMatch%20Replays"
    f"&limit={limit}&sort=latest"
)
print(f"\n→ GET {LISTING_URL}")
resp = requests.get(LISTING_URL, headers={"User-Agent": "Mozilla/5.0"})
print(f"Status = {resp.status_code}")
if resp.status_code != 200:
    sys.exit("ERROR: Failed to fetch Match Replays listing.")

# --- Step 2: Extract the __APOLLO_STATE__ JSON blob ---
match = re.search(
    r'window\.__APOLLO_STATE__\s*=\s*({.*?})\s*;\s*</script>',
    resp.text, re.DOTALL
)
if not match:
    sys.exit("ERROR: Could not find embedded Apollo state JSON.")

state_json = match.group(1)
state = json.loads(state_json)
print(f"Loaded Apollo cache with {len(state)} entries.")

# --- Step 3: Pull out video‐item records with durations ---
candidates = []
for entry in state.values():
    if not isinstance(entry, dict):
        continue

    # Look for a duration field
    dur_sec = None
    if "durationInSeconds" in entry:
        dur_sec = entry["durationInSeconds"]
    elif "duration" in entry and isinstance(entry["duration"], str):
        dur_sec = parse_duration(entry["duration"])
    elif "duration" in entry and isinstance(entry["duration"], (int, float)):
        dur_sec = int(entry["duration"])

    if not dur_sec or dur_sec < 3600:
        continue

    vid_id = entry.get("id") or entry.get("videoId")
    slug   = entry.get("slug")
    if not vid_id or not slug:
        continue

    url = f"https://www.afl.com.au/video/{vid_id}/{slug}"
    candidates.append((dur_sec, url))

print(f"Found {len(candidates)} full-match replays (≥1 hr).")

if not candidates:
    sys.exit("No match replays ≥ 1 hr found in the Apollo cache.")

# --- Step 4: Download each via yt-dlp ---
ydl_opts = {
    "outtmpl": os.path.join(DL_DIR, f"{label} - %(title)s.%(ext)s"),
    "format":  "bestvideo+bestaudio/best",
    "noprogress": True,
}

for dur, replay_url in sorted(candidates, key=lambda x: -x[0]):
    m = f"{dur//3600:d}h{(dur%3600)//60:02d}m"
    print(f"\n→ yt-dlp downloading ({m}): {replay_url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([replay_url])
    except Exception as e:
        print(f"ERROR downloading {replay_url}: {e}")

print("\nAll done!")
