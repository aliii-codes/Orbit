import schedule
import time
from github_fetcher import fetch_repo_data
from digest_generator import generate_digest
from emailer import send_digest
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "Frontend", "data", "config.json")

def load_email():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
    return config.get("email", "")

def run_digest():
    print("Running GitHub Digest Agent...")
    
    email = load_email()
    if not email:
        print("Error: No email found in config.json")
        return

    data = fetch_repo_data()
    digest = generate_digest(data)
    send_digest(email, digest)
    print("Digest sent successfully!")

def start_scheduler():
    schedule.every().day.at("08:00").do(run_digest)
    print("Scheduler started — digest will run at 8:00 AM daily")

    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    run_digest()  