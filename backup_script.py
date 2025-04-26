import os
import shutil
import schedule
import time
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import logging

logging.basicConfig(
    filename='backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

load_dotenv()

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
APP_PASSWORD = os.getenv('APP_PASSWORD')
RECEIVER_EMAIL = os.getenv('RECEIVER_EMAIL')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

DATABASE_DIR = "databases"
BACKUP_DIR = "backups"

def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.send_message(msg)
    
    
    logging.info("Email sent")

def backup_databases():
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_subdir = os.path.join(BACKUP_DIR, timestamp)
    os.makedirs(backup_subdir)

    backup_files = []
    for file in os.listdir(DATABASE_DIR):
        if file.endswith(('.sql', '.sqlite3')):
            src = os.path.join(DATABASE_DIR, file)
            dst = os.path.join(backup_subdir, file)
            shutil.copy(src, dst)
            backup_files.append(file)
            logging.info(f"Backed up: {file}")


    if backup_files:
        subject = "Backup Success"
        body = "Files backed up:\n" + "\n".join(backup_files)
        send_email(subject, body)
    else:
        subject = "Backup Warning"
        body = "No database files found in " + DATABASE_DIR
        send_email(subject, body)

    logging.info("Backup finished")


schedule.every().day.at("00:00").do(backup_databases)


def main():
    logging.info("Starting backup")
    backup_databases()
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()