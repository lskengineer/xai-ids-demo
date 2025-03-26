from dash import Dash, html, dcc, Input, Output
from pymongo import MongoClient
import plotly.graph_objs as go
from dotenv import load_dotenv
from bson import ObjectId
import os

# Load environment variables
load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client.ids

app = Dash(__name__)
app.title = "Explainable IDS"

# Bright color mapping
COLOR_MAP = {
    "benign": "#00cc44", "dos_hulk": "#ff3333", "dos_slowloris": "#ff6600",
    "dos_slowhttptest": "#ff9966", "dos_golden_eye": "#ffcc00", "heartbleed": "#cc0000",
    "portscan": "#00bfff", "ssh_patator": "#cc66ff", "ftp_patator": "#9966cc",
    "botnet_ares": "#ff66cc", "ddos_loit": "#ff0066", "web_brute_force": "#ff6699",
    "web_sql_injection": "#3366ff", "web_xss": "#00cccc", "unknown": "gray"
}

def get_color(pred):
    return COLOR_MAP.get(str(pred).lower(), "gray")

def get_alerts():
    alerts = list(db.alerts.find().sort("_id", -1).limit(10))
    return [
        {
            "label": f"{a.get('timestamp', '')} - {a.get('prediction', 'Unknown')}",
            "value": str(a["_id"])  # ✅ Only include string-safe fields
        }
        for a in alerts
    ]

# Layout
app.layout = html.Div(style={'fontFamily': 'Arial'}, children=[
    html.H1("Explainable IDS Dashboard", style={'textAlign': 'center'}),

    html.Label("Select Alert", style={'fontWeight': 'bold'}),
    dcc.Dropdown(id='alert-dropdown'),

    html.H2(id='prediction-output', style={'textAlign': 'center'}),
    html.Div(id='recent-threats', style={'textAlign': 'center'}),

    dcc.Graph(id='shap-graph'),
    dcc.Graph(id='lime-graph'),

    dcc.Interval(id='interval-refresh', interval=15*1000, n_intervals=0)
])

@app.callback(
    Output('alert-dropdown', 'options'),
    Input('interval-refresh', 'n_intervals')
)
def update_dropdown(_):
    return get_alerts()

@app.callback(
    [Output('prediction-output', 'children'),
     Output('prediction-output', 'style'),
     Output('shap-graph', 'figure'),
     Output('lime-graph', 'figure'),
     Output('recent-threats', 'children')],
    [Input('alert-dropdown', 'value')],
)
def update_graphs(selected_id):
    if not selected_id:
        return "No alert selected", {}, {}, {}, ""

    alert = db.alerts.find_one({"_id": ObjectId(selected_id)})
    pred = alert.get("prediction", "Unknown")
    label_color = get_color(pred)

    # SHAP chart
    shap_fig = go.Figure([go.Bar(
        x=alert["shap"],
        y=list(alert["flow"].keys()),
        orientation='h',
        marker=dict(color='blue')
    )])
    shap_fig.update_layout(title="SHAP Feature Importance")

    # LIME chart
    lime_pairs = alert["lime"]
    lime_fig = go.Figure([go.Bar(
        x=[v for _, v in lime_pairs],
        y=[k for k, _ in lime_pairs],
        orientation='h',
        marker=dict(color='orange')
    )])
    lime_fig.update_layout(title="LIME Explanation")

    # Recent threats display
    recent = list(db.alerts.find().sort("_id", -1).limit(5))
    threat_tags = []
    for r in recent:
        p = r.get("prediction", "Unknown")
        color = get_color(p)
        threat_tags.append(html.Span(p, style={
            "backgroundColor": color,
            "color": "white",
            "padding": "5px 10px",
            "margin": "5px",
            "borderRadius": "5px",
            "display": "inline-block",
            "textTransform": "capitalize"
        }))

    threat_list = html.Div([
        html.H4("Recent Threats (Last 5):", style={'marginTop': '20px'}),
        html.Div(threat_tags)
    ])

    return f"Prediction: {pred}", {'color': label_color, 'fontWeight': 'bold'}, shap_fig, lime_fig, threat_list

# Run server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8050)

