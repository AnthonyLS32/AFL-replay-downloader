# AFL Replay Downloader Suite

A set of scripts and a Streamlit UI to automate downloading AFL match replays for personal offline viewing.

## Features

- Securely store AFL credentials via `keyring`
- Scrape and download today’s replays to a local folder
- Log downloaded files to prevent duplicates
- Optional email alerts on new downloads
- Streamlit interface for on-demand replay pulls
- Download buttons to grab files directly in your browser
- Mobile sync via Syncthing (see docs)

## Setup

1. Clone this repo  
2. `pip install -r requirements.txt`  
3. Copy `config.ini.example` → `config.ini` and fill in your details  
4. Run `python credential_manager.py <your_auc_password>`  
5. Test with `python downloader.py`  
6. `streamlit run streamlit_app.py` to launch the web UI  

## Disclaimer

For personal, offline use only. Redistribution or commercial use is prohibited.  
