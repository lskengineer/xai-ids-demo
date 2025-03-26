from pymongo import MongoClient
from dotenv import load_dotenv
import os
import subprocess
import requests

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.ids

SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK")

# Get last 5 alerts
alerts = list(db.alerts.find().sort('_id', -1).limit(5))
malicious_count = sum(1 for a in alerts if a["prediction"] == 1)

if malicious_count >= 3:
    print(f"� High threat level detected! ({malicious_count}/5)")

    # Retrain model
    subprocess.run(["python3", "train_model.py"])

    # Commit & push model
    subprocess.run(["git", "add", "app/model.pkl"])
    subprocess.run(["git", "commit", "-m", "� Auto-retrain: threat spike"])
    subprocess.run(["git", "push"])

    # � Send Slack alert
    if SLACK_WEBHOOK:
        requests.post(SLACK_WEBHOOK, json={
            "text": f"� *Auto-Retrain Triggered* — {malicious_count}/5 latest alerts were malicious.\n� New model deployed to production!"
        })

else:
    print(f"✅ Threat level normal ({malicious_count}/5). No retrain.")

