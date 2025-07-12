# streamlit_app.py

import streamlit as st
import subprocess
import sys
import os
import datetime

import requests
from bs4 import BeautifulSoup
import yt_dlp
import json
import io
import contextlib

st.set_page_config(page_title="AFL Replay Downloader + Tests")
st.title("AFL Replay Downloader + Embedded Micro-Tests")

# --- Existing Download UI (unchanged) ---

st.subheader("Download Full-Match Replays")
col1, col2 = st.columns(2)
with col1:
    label_date = st.date_input("Label prefix date", datetime.date.today())
with col2:
    limit = st.number_input("Max videos to fetch", 1, 200, 100, 10)

if st.button("Download Replays (>1 hr)"):
    python_exe = sys.executable
    cmd = [
        python_exe, "downloader.py",
        "--limit", str(limit),
        "--label", label_date.strftime("%Y-%m-%d")
    ]
    with st.spinner("Downloading… this may take a few minutes"):
        result = subprocess.run(cmd, capture_output=True, text=True)
    st.text_area("Download Logs", result.stdout + result.stderr, height=400)

# --- New Section: Embedded Micro-Tests ---

st.markdown("---")
st.subheader("Micro-Tests for Debugging AFL Video Fetching")

def run_and_capture(fn):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            fn()
        except Exception as e:
            print("ERROR:", e)
    return buf.getvalue()

# 1) Test fetching a single known replay page
def test_replay_page():
    url = (
        "https://www.afl.com.au/video/1362116/"
        "match-replay-gold-coast-v-collingwood"
        "?videoId=1362116&modal=true"
        "&type=video&publishFrom=1752258600001"
        "&limit=50"
        "&tagNames=ProgramCategory%3AMatch%20Replays"
        "&references=AFL_COMPSEASON%3A73%2CAFL_ROUND%3A1164"
    )
    print("URL:", url)
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    print("Status Code:", resp.status_code)
    bs = BeautifulSoup(resp.text, "html.parser")
    video_tag = bs.find("video")
    print("Video tag found:", bool(video_tag))
    for src in bs.find_all("source"):
        print(" Source src=", src.get("src"))

# 2) Test yt-dlp extraction on that URL
def test_yt_dlp():
    url = (
        "https://www.afl.com.au/video/1362116/"
        "match-replay-gold-coast-v-collingwood"
        "?videoId=1362116&modal=true"
        "&type=video&publishFrom=1752258600001"
        "&limit=50"
        "&tagNames=ProgramCategory%3AMatch%20Replays"
        "&references=AFL_COMPSEASON%3A73%2CAFL_ROUND%3A1164"
    )
    print("URL:", url)
    opts = {"quiet": False, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    print(json.dumps(info, indent=2)[:1000], "…")  # show first 1k chars

# 3) Test listing page JSON blobs
def test_listing_json():
    listing_url = (
        "https://www.afl.com.au/video?"
        "tagNames=ProgramCategory%3AMatch%20Replays&limit=10"
    )
    print("Listing URL:", listing_url)
    resp = requests.get(listing_url, headers={"User-Agent": "Mozilla/5.0"})
    print("Status Code:", resp.status_code)
    bs = BeautifulSoup(resp.text, "html.parser")
    blobs = bs.find_all("script", type="application/json")
    print("Found JSON scripts:", len(blobs))
    for i, sc in enumerate(blobs):
        try:
            data = json.loads(sc.string)
            keys = list(data.keys())
            print(f" Blob {i} top keys:", keys[:10])
        except Exception as e:
            print(f" Blob {i} parse error:", e)

# Buttons to trigger each test
if st.button("1. Test Replay Page HTML"):
    output = run_and_capture(test_replay_page)
    st.code(output, language="text")

if st.button("2. Test yt-dlp Extraction"):
    output = run_and_capture(test_yt_dlp)
    st.code(output, language="text")

if st.button("3. Test Listing Page JSON"):
    output = run_and_capture(test_listing_json)
    st.code(output, language="text")
