import streamlit as st
import subprocess
import sys
import os
import datetime

st.set_page_config(page_title="AFL Replay Downloader")
st.title("AFL Replay Downloader")

# UI: Pick date & limit
col1, col2 = st.columns(2)
with col1:
    selected_date = st.date_input(
        "Select date to label downloads", 
        datetime.date.today()
    )
with col2:
    limit = st.number_input(
        "Max videos to fetch", 
        min_value=1, max_value=100, value=10, step=1
    )

# Trigger download
if st.button("Download Replays (>1 hr)"):
    python_exe = sys.executable
    cmd = [
        python_exe, "downloader.py",
        "--date", selected_date.strftime("%Y-%m-%d"),
        "--limit", str(limit)
    ]

    with st.spinner(f"Fetching up to {limit} videos, filtering ≥1 hour…"):
        result = subprocess.run(cmd, capture_output=True, text=True)

    st.success("Done! See logs below.")
    st.text_area("Download Logs", result.stdout + result.stderr, height=400)

# Show already-downloaded files
dl_dir = "./AFL_Replays"
if os.path.isdir(dl_dir):
    st.subheader("Downloaded Replays")
    for fname in sorted(os.listdir(dl_dir)):
        file_path = os.path.join(dl_dir, fname)
        with open(file_path, "rb") as fp:
            st.download_button(
                label=fname,
                data=fp.read(),
                file_name=fname,
                mime="video/mp4"
            )
