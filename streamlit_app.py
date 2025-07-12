import streamlit as st
import subprocess
import sys
import os
import datetime

st.set_page_config(page_title="AFL Replay Downloader")
st.title("AFL Replay Downloader")

# UI: How many latest videos to fetch and label prefix
col1, col2 = st.columns(2)
with col1:
    label_date = st.date_input("Label prefix date", datetime.date.today())
with col2:
    limit = st.number_input(
        "Max videos to fetch", 
        min_value=1, max_value=200, value=100, step=10
    )

if st.button("Download Latest Full-Match Replays"):
    python_exe = sys.executable
    cmd = [
        python_exe, "downloader.py",
        "--limit", str(limit),
        "--label", label_date.strftime("%Y-%m-%d")
    ]
    with st.spinner(f"Fetching top {limit} videos and filtering ≥1 hr…"):
        result = subprocess.run(cmd, capture_output=True, text=True)

    st.success("Finished.")
    st.text_area("Download Logs", result.stdout + result.stderr, height=400)

# List anything already downloaded
dl_dir = "./AFL_Replays"
if os.path.isdir(dl_dir):
    st.subheader("Downloaded Replays")
    for fname in sorted(os.listdir(dl_dir)):
        with open(os.path.join(dl_dir, fname), "rb") as fp:
            st.download_button(
                label=fname,
                data=fp.read(),
                file_name=fname,
                mime="video/mp4"
            )
