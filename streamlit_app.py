import streamlit as st
import subprocess
import sys
import os
import datetime

st.set_page_config(page_title="AFL Replay Downloader")
st.title("AFL Replay Downloader")

# Date picker (for naming/logging only)
selected_date = st.date_input("Label downloads with date", datetime.date.today())

if st.button("Download Replays (>1 hr)"):
    python_exe = sys.executable
    cmd = [
        python_exe, "downloader.py",
        "--date", selected_date.strftime("%Y-%m-%d"),
        "--limit", "100"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    st.text_area("Logs", result.stdout + result.stderr, height=400)

# Show already-downloaded files
dl_dir = "./AFL_Replays"
if os.path.isdir(dl_dir):
    st.subheader("Downloaded Replays")
    for fname in sorted(os.listdir(dl_dir)):
        path = os.path.join(dl_dir, fname)
        with open(path, "rb") as fp:
            st.download_button(label=fname, data=fp.read(), file_name=fname, mime="video/mp4")
