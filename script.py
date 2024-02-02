import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, callback_context
from dash.dependencies import Input, Output
import requests
import pandas as pd
import plotly.graph_objs as go
import locale

# Definir localização para formatação de números
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

# Inicialização da aplicação Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Definir cores
colors = {
    'background': '#66666e',
    'text': '#000000',
    'color1': '#6a3d5a',
    'color2': '#66666e',
    'color3': '#6d8d76',
    'color4': '#b0c65a',
    'color5': '#ebf74f'
}

# Layout do dashboard
app.layout = dbc.Container(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
    html.H1("Top Moedas Digitais", style={'textAlign': 'center', 'color': '#ffff'}),
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id='crypto-dropdown',
            options=[
                {'label': 'Bitcoin', 'value': 'bitcoin'},
                {'label': 'Ethereum', 'value': 'ethereum'},
                {'label': 'Ripple', 'value': 'ripple'},
                {'label': 'Litecoin', 'value': 'litecoin'},
                {'label': 'Bitcoin Cash', 'value': 'bitcoin-cash'},
                {'label': 'Cardano', 'value': 'cardano'},
                {'label': 'Polkadot', 'value': 'polkadot'},
                {'label': 'Stellar', 'value': 'stellar'},
                {'label': 'Chainlink', 'value': 'chainlink'},
                {'label': 'Binance Coin', 'value': 'binancecoin'},
                {'label': 'Tether', 'value': 'tether'}
            ],
            value='bitcoin',
            clearable=False,
            style={'justify-content': 'center'}
        ), width=4),
        dbc.Col(dcc.Dropdown(
            id='currency-dropdown',
            options=[
                {'label': 'BRL - Real Brasileiro', 'value': 'brl'},
                {'label': 'USD - Dólar Americano', 'value': 'usd'},
                {'label': 'EUR - Euro', 'value': 'eur'},
                {'label': 'JPY - Iene Japonês', 'value': 'jpy'},
                {'label': 'GBP - Libra Esterlina', 'value': 'gbp'}
            ],
            value='usd',
            clearable=False,
            style={'justify-content': 'center'}
        ), width=4)
    ], className="mb-5", justify="center"),
    dbc.Row([
        dbc.Col(dbc.Container(html.Div(id='crypto-info-container'), style={'background-color': 'white', 'padding': '20px', 'border-radius': '5px'}), width=12, className="mb-4"),
        dbc.Col(dbc.Container(dcc.Graph(id='price-chart-container', style={'border': '1px solid gray'}), style={'background-color': 'white', 'padding': '20px', 'border-radius': '5px'}), width=12, className="mb-4"),
        dbc.Col(dbc.Container(dcc.Graph(id='volume-chart-container', style={'border': '1px solid gray'}), style={'background-color': 'white', 'padding': '20px', 'border-radius': '5px'}), width=12),
    ], className="mb-4", justify="center")
])

# Função para buscar informações da criptomoeda selecionada
def get_crypto_info(crypto):
    url = f'https://api.coingecko.com/api/v3/coins/{crypto}'
    response = requests.get(url)
    data = response.json()
    return data

# Callback para atualizar as informações da criptomoeda selecionada
@app.callback(
    [Output('crypto-info-container', 'children'),
     Output('price-chart-container', 'figure'),
     Output('volume-chart-container', 'figure')],
    [Input('crypto-dropdown', 'value'),
     Input('currency-dropdown', 'value')]
)
def update_crypto_info(selected_crypto, selected_currency):
    crypto_data = get_crypto_info(selected_crypto)
    name = crypto_data['name']
    symbol = crypto_data['symbol'].upper()
    current_price = crypto_data['market_data']['current_price'][selected_currency]
    market_cap = crypto_data['market_data']['market_cap'][selected_currency]
    volume = crypto_data['market_data']['total_volume'][selected_currency]
    price_change_percentage_24h = crypto_data['market_data']['price_change_percentage_24h']

    # Formatar valores numéricos para melhor legibilidade
    current_price_formatted = locale.currency(current_price, grouping=True, symbol=None)
    market_cap_formatted = locale.currency(market_cap, grouping=True, symbol=None)
    volume_formatted = locale.currency(volume, grouping=True, symbol=None)
    price_change_percentage_24h_formatted = f"{price_change_percentage_24h:.2f}%"

    # Criar gráfico de preços
    market_chart_data = requests.get(f'https://api.coingecko.com/api/v3/coins/{selected_crypto}/market_chart',
                                     params={'vs_currency': selected_currency, 'days': '30'})
    market_chart_data = market_chart_data.json()
    market_chart_df = pd.DataFrame(market_chart_data['prices'], columns=['time', 'price'])
    market_chart_df['time'] = pd.to_datetime(market_chart_df['time'], unit='ms')
    price_chart = go.Figure(
        data=[go.Scatter(x=market_chart_df['time'], y=market_chart_df['price'], mode='lines', name='Preço')],
        layout=go.Layout(title=f'Histórico de Preços de {name} ({symbol}) em {selected_currency.upper()}',
                         xaxis_title='Data',
                         yaxis_title=f'Preço em {selected_currency.upper()}',
                         plot_bgcolor='white',
                         paper_bgcolor='white',
                         font=dict(color=colors['text']))
    )

    # Criar gráfico de volume
    market_chart_volume_df = pd.DataFrame(market_chart_data['total_volumes'], columns=['time', 'volume'])
    market_chart_volume_df['time'] = pd.to_datetime(market_chart_volume_df['time'], unit='ms')
    volume_chart = go.Figure(
        data=[go.Bar(x=market_chart_volume_df['time'], y=market_chart_volume_df['volume'], name='Volume')],
        layout=go.Layout(title=f'Volume de Negociação de {name} ({symbol}) em {selected_currency.upper()}',
                         xaxis_title='Data',
                         yaxis_title=f'Volume em {selected_currency.upper()}',
                         plot_bgcolor='white',
                         paper_bgcolor='white',
                         font=dict(color=colors['text']))
    )

    # Criar container com as informações
    info_container = html.Div([
        html.H2(f"{name} ({symbol})", style={'color': colors['color4'], 'textAlign': 'center'}),
        html.P(f"Preço atual: {current_price_formatted}", style={'textAlign': 'center', 'color': colors['text']}),
        html.P(f"Capitalização de mercado: {market_cap_formatted}", style={'textAlign': 'center', 'color': colors['text']}),
        html.P(f"Volume de 24h: {volume_formatted}", style={'textAlign': 'center', 'color': colors['text']}),
        html.P(f"Variação percentual (24h): {price_change_percentage_24h_formatted}", style={'textAlign': 'center', 'color': colors['text']})
    ])

    return info_container, price_chart, volume_chart

# Execução do aplicativo
if __name__ == '__main__':
    app.run_server(debug=True)
