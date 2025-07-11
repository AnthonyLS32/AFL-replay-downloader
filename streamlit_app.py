import streamlit as st
import os
import configparser

st.set_page_config(page_title="AFL Replay Downloader")
st.title("AFL Replay Downloader")

# Step 1: Credentials
if "creds_set" not in st.session_state:
    st.subheader("Step 1: Enter AFL Login")
    st.text_input("AFL Username/Email", key="username")
    st.text_input("AFL Password", type="password", key="password")

    if st.button("Save Credentials"):
        username = st.session_state.username
        password = st.session_state.password

        cfg = configparser.ConfigParser()
        cfg['afl'] = {
            'username':     username,
            'password':     password,
            'password_key': 'AFL_PW'
        }
        cfg['paths'] = {
            'download_folder': r'C:\AFL_Replays',
            'log_file':        r'C:\AFL_Replays\download_log.txt'
        }
        cfg['email'] = {
            'smtp_server': 'smtp.example.com',
            'smtp_port':   '587',
            'from_addr':   'your.email@example.com',
            'to_addr':     'anthonylasala@hotmail.com',
            'subject':     'New AFL Replay Downloaded'
        }
        cfg['sync'] = {
            'syncthing_folder': r'C:\AFL_Replays'
        }

        with open('config.ini', 'w') as f:
            cfg.write(f)

        st.success("Credentials saved to config.ini.")
        st.session_state.creds_set = True

# Step 2: Download UI
if "creds_set" in st.session_state:
    st.subheader("Step 2: Download Replays")
    selected_date = st.date_input("Select date to download")

    if st.button("Download Replays"):
        # Run downloader.py and show its output
        cmd = [
            "python", "downloader.py",
            "--date", selected_date.strftime("%Y-%m-%d")
        ]
        result = os.popen(" ".join(cmd)).read()
        st.text(result)

    # List and serve downloaded files
    dl_folder = r"C:\AFL_Replays"
    if os.path.isdir(dl_folder):
        st.subheader("Downloaded Replays")
        for fname in sorted(os.listdir(dl_folder)):
            path = os.path.join(dl_folder, fname)
            with open(path, "rb") as fp:
                st.download_button(label=fname, data=fp, file_name=fname, mime="video/mp4")
