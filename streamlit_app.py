import streamlit as st
import subprocess
import os
import configparser

# --- UI: Credentials ---
st.title("AFL Replay Downloader")

if "creds_set" not in st.session_state:
    st.subheader("Step 1: Enter AFL Login")
    st.session_state.username = st.text_input("AFL Username/Email", key="username")
    st.session_state.password = st.text_input("AFL Password", type="password", key="password")
    if st.button("Save Credentials"):
        # write config.ini
        cfg = configparser.ConfigParser()
        cfg['afl'] = {
            'username': st.session_state.username,
            'password_key': 'AFL_PW'
        }
        # you can edit these defaults or pull from config.ini.example
        cfg['paths'] = {
            'download_folder': 'C:\\AFL_Replays',
            'log_file':      'C:\\AFL_Replays\\download_log.txt'
        }
        cfg['email'] = {
            'smtp_server': 'smtp.example.com',
            'smtp_port':    '587',
            'from_addr':    'your.email@example.com',
            'to_addr':      'anthonylasala@hotmail.com',
            'subject':      'New AFL Replay Downloaded'
        }
        cfg['sync'] = {
            'syncthing_folder': 'C:\\AFL_Replays'
        }

        with open('config.ini', 'w') as f:
            cfg.write(f)

        # store password in keyring
        subprocess.run([
            "python", "credential_manager.py", st.session_state.password
        ], check=True)

        st.success("Credentials saved to config.ini and keyring.")
        st.session_state.creds_set = True

# --- UI: Date picker & Download ---
if "creds_set" in st.session_state:
    st.subheader("Step 2: Download Replays")
    date = st.date_input("Select date to download", )
    if st.button("Download Replays"):
        # call downloader with --date
        cmd = [
            "python", "downloader.py",
            "--date", date.strftime("%Y-%m-%d")
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        st.text(result.stdout or result.stderr)

    # list existing files for quick download
    dl_folder = os.path.expandvars("C:\\AFL_Replays")
    if os.path.isdir(dl_folder):
        st.subheader("Downloaded Replays")
        for fname in sorted(os.listdir(dl_folder)):
            path = os.path.join(dl_folder, fname)
            with open(path, "rb") as fp:
                data = fp.read()
            st.download_button(fname, data, file_name=fname)
