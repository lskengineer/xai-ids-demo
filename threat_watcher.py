# threat_watcher.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os
import subprocess

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.ids

# Get latest 5 alerts
alerts = list(db.alerts.find().sort('_id', -1).limit(5))
malicious_count = sum(1 for a in alerts if a["prediction"] == 1)

if malicious_count >= 3:
    print(f"íº¨ High threat level detected! ({malicious_count}/5)")

    # Step 1: Retrain the model
    subprocess.run(["python3", "train_model.py"])

    # Step 2: Commit and push model.pkl to GitHub
    subprocess.run(["git", "add", "app/model.pkl"])
    subprocess.run(["git", "commit", "-m", "í´– Auto-retrain due to threat spike"])
    subprocess.run(["git", "push"])
else:
    print(f"âœ… Threat level normal ({malicious_count}/5). No retrain needed.")

