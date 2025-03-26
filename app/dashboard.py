from dash import Dash, html, dcc, Input, Output
from pymongo import MongoClient
import plotly.graph_objs as go
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.ids

app = Dash(__name__)
app.title = "Explainable IDS"

# Layout with dynamic elements
app.layout = html.Div(style={'fontFamily': 'Arial'}, children=[
    html.H1("Explainable IDS Dashboard", style={'textAlign': 'center'}),

    # Ì¥Å Prediction label
    html.H2(id='prediction-output', style={'textAlign': 'center'}),

    # Ì≥ä SHAP chart
    dcc.Graph(id='shap-graph'),

    # Ì≥ä LIME chart
    dcc.Graph(id='lime-graph'),

    # ‚è≤Ô∏è Auto-refresh interval: every 10 sec
    dcc.Interval(
        id='interval-component',
        interval=10 * 1000,  # 10,000 ms = 10 seconds
        n_intervals=0
    )
])

# Callback to update the dashboard every interval
@app.callback(
    [Output('prediction-output', 'children'),
     Output('prediction-output', 'style'),
     Output('shap-graph', 'figure'),
     Output('lime-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    latest = db.alerts.find_one(sort=[('_id', -1)])

    # Ì¥ç Prediction
    label = "Malicious" if latest["prediction"] == 1 else "Benign"
    label_color = "red" if latest["prediction"] == 1 else "green"

    # Ì≥ä SHAP values
    shap_features = list(latest["flow"].keys())
    shap_values = latest["shap"]
    shap_chart = go.Figure([go.Bar(
        x=shap_values,
        y=shap_features,
        orientation='h',
        marker=dict(color='blue')
    )])
    shap_chart.update_layout(title="SHAP Feature Importance", height=400)

    # Ì≥ä LIME values
    lime_keys = [pair[0] for pair in latest["lime"]]
    lime_vals = [pair[1] for pair in latest["lime"]]
    lime_chart = go.Figure([go.Bar(
        x=lime_vals,
        y=lime_keys,
        orientation='h',
        marker=dict(color='orange')
    )])
    lime_chart.update_layout(title="LIME Explanation", height=400)

    return f"Prediction: {label}", {'color': label_color}, shap_chart, lime_chart

# Run the app
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050)

