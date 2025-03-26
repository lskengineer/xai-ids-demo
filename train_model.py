import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib
from pymongo import MongoClient
from datetime import datetime

# Optional: log retrain in MongoDB
client = MongoClient("mongodb://192.168.0.119:27017")
db = client.ids
db.retrain_log.insert_one({"time": datetime.utcnow(), "event": "Auto-retrain triggered"})

# Load and train
df = pd.read_csv("app/sample_flows.csv")
X = df.drop(columns=["Label"])
y = df["Label"]

# Train a simple classifier
model = RandomForestClassifier()
model.fit(X, y)

# Save the model
joblib.dump(model, "app/model.pkl")
print("✅ model.pkl saved successfully!")

