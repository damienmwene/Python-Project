import requests
import time
import os
import logging
from datetime import datetime

# Configure logging to both console and file
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.StreamHandler(),                      # Console (stdout)
        logging.FileHandler("uptime_log.txt")         # File
    ]
)

# List of URLs to monitor
URLS = [
    "https://www.google.com",
    "https://auu5wso6vs2eev42dwt47b35he0geulm.lambda-url.us-east-1.on.aws"
]

# Slack webhook URL (set as environment variable)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Send alert to Slack
def send_slack_alert(url):
    if not SLACK_WEBHOOK_URL:
        logging.warning("Slack webhook URL not configured.")
        return
    message = {
        "text": f":red_circle: ALERT: {url} is DOWN!"
    }
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        if response.status_code != 200:
            logging.warning(f"Slack alert failed: {response.text}")
    except Exception as e:
        logging.error(f"Slack alert error: {e}")

# Function to check a single URL
def check_website(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# Main monitoring loop
def monitor():
    while True:
        for url in URLS:
            status = check_website(url)
            status_str = "UP" if status else "DOWN"
            logging.info(f"{url} is {status_str}")
            if not status:
                send_slack_alert(url)
        logging.info("Waiting 60 seconds before next check...\n")
        time.sleep(60)

if __name__ == "__main__":
    monitor()
