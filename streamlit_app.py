import streamlit as st
import subprocess
import os

st.title("AFL Replay Downloader")

# Prompt for AFL credentials
if 'pw_set' not in st.session_state:
    pw = st.text_input("Enter your AFL password", type="password")
    if st.button("Store Credentials"):
        subprocess.run(["python", "credential_manager.py", pw])
        st.session_state.pw_set = True
        st.success("Credentials stored securely!")

# Date selector and download button
date = st.date_input("Select date to download replays")
if st.button("Download Replays"):
    cmd = ["python", "downloader.py", "--date", date.strftime("%Y-%m-%d")]
    result = subprocess.run(cmd, capture_output=True, text=True)
    st.text(result.stdout)

# List downloaded files for direct download
folder = os.path.expanduser("C:\\AFL_Replays")
if os.path.isdir(folder):
    st.subheader("Downloaded Replays")
    for fname in sorted(os.listdir(folder)):
        path = os.path.join(folder, fname)
        with open(path, "rb") as f:
            data = f.read()
        st.download_button(label=fname, data=data, file_name=fname)
