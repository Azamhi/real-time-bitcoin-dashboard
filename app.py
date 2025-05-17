import dash
from dash import dcc, html
import requests
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import datetime

# Initialize app
app = dash.Dash(__name__)
server = app.server  # For deployment (e.g., Render)

# Function to fetch Bitcoin data from CoinGecko
def fetch_crypto_data():
    url = 'https://api.coingecko.com/api/v3/coins/bitcoin/market_chart'
    params = {
        'vs_currency': 'usd',
        'days': '30'  # Don't specify interval; hourly is returned automatically for days between 2–90
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()  # Raises HTTPError for bad responses
        data = r.json()
        if 'prices' not in data:
            raise ValueError("Missing 'prices' in API response.")
        prices = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
        prices['timestamp'] = pd.to_datetime(prices['timestamp'], unit='ms')
        return prices
    except Exception as e:
        print("❌ Error fetching data:", e)
        return pd.DataFrame(columns=['timestamp', 'price'])

# Layout
app.layout = html.Div([
    html.H1("🚀 Real-Time Bitcoin Market Dashboard", style={'textAlign': 'center'}),
    dcc.Interval(id='refresh-interval', interval=60*1000, n_intervals=0),
    dcc.Graph(id='live-price-graph'),
    html.Div(id='latest-price', style={'fontSize': 24, 'textAlign': 'center', 'marginTop': 10})
])

# Callback to update graph and latest price
@app.callback(
    [Output('live-price-graph', 'figure'),
     Output('latest-price', 'children')],
    [Input('refresh-interval', 'n_intervals')]
)
def update_graph(n):
    df = fetch_crypto_data()
    if df.empty:
        fig = go.Figure()
        fig.update_layout(title='⚠️ No Data Available (API error)', xaxis_title='Time', yaxis_title='USD')
        return fig, "❌ Failed to fetch price data from CoinGecko API."

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['price'],
        mode='lines+markers',
        name='BTC Price'
    ))
    fig.update_layout(
        title='Bitcoin Price - Last 30 Days',
        xaxis_title='Time',
        yaxis_title='USD'
    )

    latest_price = df.iloc[-1]['price']
    latest_time = df.iloc[-1]['timestamp']
    return fig, f"💲 Latest Price (USD): {latest_price:.2f} at {latest_time.strftime('%Y-%m-%d %H:%M:%S')}"

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
