from pymongo import MongoClient
import pandas as pd
import joblib
import shap
import lime.lime_tabular
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Load the model
model_path = "model.pkl"
model = joblib.load(model_path)
print(f"âœ… Loaded model from: {model_path}")

# Load sample flow data
csv_path = "sample_flows.csv"
df = pd.read_csv(csv_path)
X = df.drop(columns=["Label"])
y = df["Label"]
preds = model.predict(X)
print(f"í·  Made predictions on {len(X)} flows")

# Initialize SHAP and LIME explainers
shap_explainer = shap.Explainer(model.predict, X)
lime_explainer = lime.lime_tabular.LimeTabularExplainer(
    X.values,
    feature_names=X.columns.tolist(),
    class_names=["Benign", "Malicious"],
    verbose=False
)

# MongoDB Connection
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client.ids

# Insert prediction and explanations for each flow (first 3 only for demo)
for i in range(min(3, len(X))):
    shap_values = shap_explainer(X.iloc[i:i+1])
    lime_exp = lime_explainer.explain_instance(
        X.iloc[i].values, model.predict_proba, num_features=5
    )

    alert = {
        "flow": X.iloc[i].to_dict(),
        "true_label": int(y.iloc[i]),
        "prediction": int(preds[i]),
        "shap": shap_values[0].values.tolist(),
        "lime": lime_exp.as_list(),
        "timestamp": datetime.utcnow()
    }

    db.alerts.insert_one(alert)
    print(f"âœ… Inserted alert #{i+1}: Prediction={alert['prediction']}")

print("íº€ Finished model_runner.py execution")

