import smtplib
import configparser
from email.mime.text import MIMEText

cfg = configparser.ConfigParser()
cfg.read('config.ini')

smtp_server = cfg['email']['smtp_server']
smtp_port   = int(cfg['email']['smtp_port'])
from_addr   = cfg['email']['from_addr']
to_addr     = cfg['email']['to_addr']
subject     = cfg['email']['subject']

def send_alert(filename):
    body = f"New AFL replay downloaded:\n\n{filename}"
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    with smtplib.SMTP(smtp_server, smtp_port) as s:
        s.starttls()
        s.send_message(msg)
        print("Email alert sent.")

# In downloader.py, after each download:
# send_alert(filename)
