from pymongo import MongoClient
from dotenv import load_dotenv
import os
import random
from datetime import datetime

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.ids

# Generate random flow features
def fake_flow():
    return {
        "Flow Duration": random.randint(10000, 50000),
        "Total Fwd Packets": random.randint(5, 100),
        "Packet Length Mean": random.uniform(40, 100),
    }

# Insert 1 malicious record
db.alerts.insert_one({
    "flow": fake_flow(),
    "prediction": 1,
    "shap": [random.uniform(0.1, 0.4)] * 3,
    "lime": [("Flow Duration > 30000", 0.2), ("Packet Length Mean > 50", 0.25)],
    "time": datetime.utcnow()
})

print("Inserted simulated malicious alert.")

