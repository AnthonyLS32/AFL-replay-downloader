import streamlit as st
import subprocess, os

st.title("AFL Replay Downloader")

# Load or prompt for credentials
if "credentials" not in st.session_state:
    st.session_state.credentials = st.text_input("Enter your AFL password", type="password")

if st.button("Store Credentials"):
    subprocess.run(["python", "credential_manager.py", st.session_state.credentials])
    st.success("Credentials stored securely!")

# Date selector and download trigger
date = st.date_input("Select date to download replays")
if st.button("Download Today's Replays"):
    cmd = ["python", "downloader.py", "--date", date.strftime("%Y-%m-%d")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    st.text(result.stdout)

# Provide downloaded files as Streamlit downloads
from streamlit_download_button import download_button
folder = os.path.expanduser("~/AFL_Replays")
for fname in os.listdir(folder):
    path = os.path.join(folder, fname)
    with open(path, "rb") as f:
        data = f.read()
    download_button(data, fname, f"Download {fname}")
