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

def find_videos(obj):
    """Yield any dict with keys id, slug, durationInSeconds."""
    if isinstance(obj, dict):
        if "id" in obj and "slug" in obj and "durationInSeconds" in obj:
            yield obj
        for v in obj.values():
            yield from find_videos(v)
    elif isinstance(obj, list):
        for item in obj:
            yield from find_videos(item)

# --- CLI args ---
p = argparse.ArgumentParser()
p.add_argument("--limit", type=int, default=100,
               help="How many replay tiles the page requests")
p.add_argument("--label", type=str, default="latest",
               help="Prefix for saved filenames (e.g. date)")
args = p.parse_args()

limit = args.limit
label = args.label
DL_DIR = "./AFL_Replays"
os.makedirs(DL_DIR, exist_ok=True)

print(f"Fetch limit      = {limit}")
print(f"Filename prefix  = {label}")
print(f"Download folder  = {DL_DIR}")

# --- Step 1: GET the Match Replays listing page ---
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

# --- Step 2: Extract the Next.js JSON from __NEXT_DATA__ ---
soup = BeautifulSoup(resp.text, "html.parser")
script = soup.find("script", {"id": "__NEXT_DATA__", "type": "application/json"})
if not script or not script.string:
    sys.exit("ERROR: Could not find __NEXT_DATA__ JSON.")

data = json.loads(script.string)
print("Loaded __NEXT_DATA__ JSON blob")

# --- Step 3: Recursively find all video nodes with durations ---
videos = list(find_videos(data))
print(f"Scanned JSON, found {len(videos)} video nodes in total")

# --- Step 4: Filter for full‐match replays ≥ 1 hour (3600s) ---
full_replays = [
    v for v in videos
    if isinstance(v.get("durationInSeconds"), (int, float))
    and v["durationInSeconds"] >= 3600
]
print(f"Filtered down to {len(full_replays)} full‐match replays")

if not full_replays:
    sys.exit("No full‐match replays ≥1 hr found in the JSON blob.")

# --- Step 5: Build URLs and download via yt-dlp ---
ydl_opts = {
    "outtmpl": os.path.join(DL_DIR, f"{label} - %(title)s.%(ext)s"),
    "format":  "bestvideo+bestaudio/best",
    "noprogress": True,
}

for v in full_replays:
    vid_id = v["id"]
    slug   = v["slug"]
    secs   = v["durationInSeconds"]
    mm, ss = divmod(secs, 60)
    hh, mm = divmod(mm, 60)
    dur_label = f"{int(hh)}h{int(mm):02d}m"
    url = f"https://www.afl.com.au/video/{vid_id}/{slug}"
    print(f"\n→ yt-dlp downloading ({dur_label}): {url}")
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print(f"ERROR downloading {url}: {e}")

print("\nAll done!")
