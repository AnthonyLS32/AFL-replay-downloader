import argparse
import os
import sys
import yt_dlp
import datetime

# --- CLI args ---
parser = argparse.ArgumentParser()
parser.add_argument("--limit", type=int, default=100,
                    help="How many latest videos to fetch")
parser.add_argument("--label", type=str, default="latest",
                    help="Filename prefix (e.g. date label)")
args = parser.parse_args()

limit = args.limit
label = args.label
DL_DIR = "./AFL_Replays"
os.makedirs(DL_DIR, exist_ok=True)

print(f"Fetch limit      = {limit}")
print(f"Filename prefix  = {label}")
print(f"Download folder  = {DL_DIR}")

# 1) Build the listing URL
LISTING_URL = (
    f"https://www.afl.com.au/video"
    f"?tagNames=ProgramCategory%3AMatch%20Replays"
    f"&limit={limit}&sort=latest"
)
print(f"\n→ Extracting playlist from: {LISTING_URL}")

# 2) First pass: flat‐extract metadata only
flat_opts = {
    "extract_flat": True,
    "dump_single_json": True,
    "skip_download": True,
    "quiet": True,
}
with yt_dlp.YoutubeDL(flat_opts) as ydl:
    info = ydl.extract_info(LISTING_URL, download=False)

entries = info.get("entries", [])
print(f"Found {len(entries)} total entries in playlist")

# 3) Filter for full-match (duration ≥ 3600s)
candidates = []
for e in entries:
    dur = e.get("duration")
    if dur and dur >= 3600:
        url = e.get("url")
        if not url.startswith("http"):
            url = "https://www.afl.com.au" + url
        candidates.append((dur, url))

print(f"Filtered to {len(candidates)} entries ≥ 1 hour")

if not candidates:
    sys.exit("No full-match replays found. Exiting.")

# 4) Second pass: download each candidate
download_opts = {
    "outtmpl": os.path.join(DL_DIR, f"{label} - %(title)s.%(ext)s"),
    "format": "bestvideo+bestaudio/best",
}
for dur, url in candidates:
    hrs, rem = divmod(dur, 3600)
    mins, _ = divmod(rem, 60)
    dur_label = f"{int(hrs)}h{int(mins):02d}m"
    print(f"\n→ Downloading ({dur_label}): {url}")
    try:
        with yt_dlp.YoutubeDL(download_opts) as ydl:
            ydl.download([url])
    except Exception as err:
        print(f"ERROR downloading {url}: {err}")

print("\nAll done!")
