import streamlit as st
import subprocess
import os
import configparser

st.set_page_config(page_title="AFL Replay Downloader")
st.title("AFL Replay Downloader")

# Step 1: Credentials
if "creds_set" not in st.session_state:
    st.subheader("Step 1: Enter AFL Login")
    st.text_input("Username/Email", key="username")
    st.text_input("Password", type="password", key="password")

    if st.button("Save Credentials"):
        cfg = configparser.ConfigParser()
        cfg['paths'] = {
            'download_folder': './AFL_Replays',
            'log_file':        './AFL_Replays/download_log.txt'
        }
        cfg['afl'] = {
            'username':     st.session_state.username,
            'password':     st.session_state.password,
            'password_key': 'AFL_PW'
        }
        cfg['email'] = {
            'smtp_server': 'smtp.example.com',
            'smtp_port':   '587',
            'from_addr':   'your.email@example.com',
            'to_addr':     'anthonylasala@hotmail.com',
            'subject':     'New AFL Replay Downloaded'
        }
        cfg['sync'] = {'syncthing_folder': './AFL_Replays'}

        with open('config.ini', 'w') as f:
            cfg.write(f)

        st.success("config.ini saved.")
        st.session_state.creds_set = True

# Step 2: Download UI
if "creds_set" in st.session_state:
    st.subheader("Step 2: Download Replays")
    selected_date = st.date_input("Select date to download")

    if st.button("Download Replays"):
        cmd = f"python downloader.py --date {selected_date.strftime('%Y-%m-%d')}"
        # Run and capture output
        logs = subprocess.getoutput(cmd)
        st.text_area("Logs", logs, height=300)

    # Show downloaded files
    if os.path.isdir("./AFL_Replays"):
        st.subheader("Downloaded Replays")
        for fname in sorted(os.listdir("./AFL_Replays")):
            path = os.path.join("./AFL_Replays", fname)
            with open(path, "rb") as fp:
                st.download_button(fname, fp.read(), file_name=fname, mime="video/mp4")
