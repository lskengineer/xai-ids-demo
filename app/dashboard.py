import dash
from dash import html

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Explainable IDS"),
    html.P("SHAP and LIME will show here."),
])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050)

