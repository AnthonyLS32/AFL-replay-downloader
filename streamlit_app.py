import streamlit as st
import subprocess
import os
import configparser

st.set_page_config(page_title="AFL Replay Downloader")

st.title("AFL Replay Downloader")

# Step 1: Credentials
if "creds_set" not in st.session_state:
    st.subheader("Step 1: Enter AFL Login")

    # These two calls automatically store inputs in session_state["username"] and ["password"]
    st.text_input("AFL Username/Email", key="username")
    st.text_input("AFL Password", type="password", key="password")

    if st.button("Save Credentials"):
        # Read them back from session_state
        username = st.session_state.username
        password = st.session_state.password

        # Build config.ini
        cfg = configparser.ConfigParser()
        cfg['afl'] = {
            'username': username,
            'password_key': 'AFL_PW'
        }
        cfg['paths'] = {
            'download_folder': r'C:\AFL_Replays',
            'log_file':       r'C:\AFL_Replays\download_log.txt'
        }
        cfg['email'] = {
            'smtp_server': 'smtp.example.com',
            'smtp_port':    '587',
            'from_addr':    'your.email@example.com',
            'to_addr':      'anthonylasala@hotmail.com',
            'subject':      'New AFL Replay Downloaded'
        }
        cfg['sync'] = {
            'syncthing_folder': r'C:\AFL_Replays'
        }

        with open('config.ini', 'w') as f:
            cfg.write(f)

        # Store password securely
        subprocess.run(
            ["python", "credential_manager.py", password],
            check=True
        )

        st.success("Credentials saved to config.ini and keyring.")
        st.session_state.creds_set = True

# Step 2: Download UI
if "creds_set" in st.session_state:
    st.subheader("Step 2: Download Replays")

    # Date picker
    selected_date = st.date_input("Select date to download")

    if st.button("Download Replays"):
        # Call downloader.py with --date argument
        cmd = [
            "python", "downloader.py",
            "--date", selected_date.strftime("%Y-%m-%d")
        ]
        process = subprocess.run(cmd, capture_output=True, text=True)
        # Show stdout or stderr
        st.text(process.stdout or process.stderr)

    # Show already-downloaded files as download buttons
    dl_folder = r"C:\AFL_Replays"
    if os.path.isdir(dl_folder):
        st.subheader("Downloaded Replays")
        for fname in sorted(os.listdir(dl_folder)):
            file_path = os.path.join(dl_folder, fname)
            with open(file_path, "rb") as fp:
                data = fp.read()
            st.download_button(
                label=fname,
                data=data,
                file_name=fname,
                mime="video/mp4"
            )
