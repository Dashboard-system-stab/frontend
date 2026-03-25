# graph.py
import json
import plotly
import pandas as pd
import plotly.graph_objs as go
from dash import dcc, html, no_update
from dash.dependencies import Output, Input, State
from styles import INPUT_STYLE, BUTTON_STYLE, PANEL_STYLE

server_state = {
    'dates': [],
    'temps': [],
}
data_queue = []

# ---------- Лейаут ----------
graph_layout = html.Div([
    dcc.Graph(id='live-graph', animate=True),

    html.Div([
        # Таблица данных
        html.Div(id='data-panel', style={**PANEL_STYLE, 'width': 'fit-content'}),

        # Поля X, Y и кнопка
        html.Div([
            html.Div('Отправить на бэкенд', style={'fontWeight': 'bold', 'marginBottom': '12px', 'fontSize': '14px'}),
            html.Div('X', style={'fontSize': '13px', 'marginBottom': '4px'}),
            dcc.Input(id='input-x', type='text', placeholder='Введите X', style=INPUT_STYLE, debounce=False),
            html.Div('Y', style={'fontSize': '13px', 'marginTop': '10px', 'marginBottom': '4px'}),
            dcc.Input(id='input-y', type='text', placeholder='Введите Y', style=INPUT_STYLE, debounce=False),
            html.Button('Подтвердить', id='confirm-btn', n_clicks=0, style=BUTTON_STYLE),
            html.Div(id='input-error', style={'color': 'red', 'fontSize': '13px', 'marginTop': '8px', 'minHeight': '18px'}),
            html.Div(id='input-success', style={'color': 'green', 'fontSize': '13px', 'marginTop': '4px', 'minHeight': '18px'}),
        ], style={**PANEL_STYLE, 'width': '220px', 'flexShrink': '0'}),

    ], style={'display': 'flex', 'gap': '20px', 'marginTop': '20px', 'alignItems': 'flex-start'}),

    html.Div(id='debug-info', style={'marginTop': 20, 'fontSize': 16}),
    dcc.Interval(id='graph-update', interval=3000, n_intervals=0),
])


# ---------- Колбэки ----------
def register_graph_callbacks(app):

    # График
    @app.callback(
        [Output('live-graph', 'figure'),
         Output('data-panel', 'children'),
         Output('debug-info', 'children')],
        [Input('graph-update', 'n_intervals')]
    )
    def update_graph_scatter(n):
        if data_queue:
            item = data_queue.pop(0)
            server_state['dates'].append(item['date'])
            server_state['temps'].append(float(item['temperature']))

        dates = server_state['dates']
        temps = server_state['temps']

        if not dates:
            empty_layout = go.Layout(
                title='Прогноз погоды',
                xaxis=dict(title='Дата'),
                yaxis=dict(title='Температура (°C)'),
            )
            return {'data': [], 'layout': empty_layout}, html.Div('Ожидание данных...'), ""

        plot_dates = pd.to_datetime(dates)
        data = plotly.graph_objs.Scatter(
            x=plot_dates, y=temps, name='Температура',
            mode='lines+markers', line=dict(color='red', width=2), marker=dict(size=8)
        )
        layout = go.Layout(
            title='Прогноз погоды',
            xaxis=dict(title='Дата', range=[plot_dates.min(), plot_dates.max()]),
            yaxis=dict(title='Температура (°C)', range=[min(temps) - 2, max(temps) + 2]),
            showlegend=True,
            transition={'duration': 800, 'easing': 'cubic-in-out'}
        )
        return {'data': [data], 'layout': layout}, create_minimal_panel(dates, temps), ""

    # Отправка X и Y на бэкенд
    @app.callback(
        Output('ws', 'send'),
        Output('input-error', 'children'),
        Output('input-success', 'children'),
        Input('confirm-btn', 'n_clicks'),
        State('input-x', 'value'),
        State('input-y', 'value'),
        prevent_initial_call=True
    )
    def send_to_backend(n_clicks, x_val, y_val):
        if not x_val or not y_val or x_val.strip() == '' or y_val.strip() == '':
            return no_update, 'Ошибка: заполните оба поля', ''
        try:
            x = float(x_val.strip())
            y = float(y_val.strip())
        except ValueError:
            return no_update, 'Ошибка: введите числа', ''
        return json.dumps({'type': 'coefficients', 'x': x, 'y': y}), '', 'Успешно выполнено'

    # Приём данных от бэкенда
    @app.callback(
        Output('ws', 'state'),
        Input('ws', 'message'),
        prevent_initial_call=True
    )
    def receive_from_backend(message):
        if message is None:
            return no_update
        try:
            data = json.loads(message['data'])
            if 'temperature' in data:
                data_queue.append(data)
        except (json.JSONDecodeError, KeyError, TypeError):
            pass
        return no_update


# ---------- Таблица ----------
def create_minimal_panel(dates, temps):
    header = html.Div([
        html.Span('Дата', style={'width': '120px', 'display': 'inline-block', 'fontWeight': 'bold', 'marginBottom': '5px'}),
        html.Span('Температура', style={'width': '100px', 'display': 'inline-block', 'fontWeight': 'bold', 'marginBottom': '5px'})
    ], style={'marginBottom': '10px'})
    rows = [header]
    for date_str, temp in zip(dates, temps):
        date_label = pd.to_datetime(date_str).strftime('%d.%m.%Y')
        row = html.Div([
            html.Span(date_label, style={'width': '120px', 'display': 'inline-block'}),
            html.Span(f"{temp:.1f}°C", style={'width': '100px', 'display': 'inline-block'})
        ], style={'padding': '3px 0', 'fontFamily': 'Arial', 'fontSize': '14px'})
        rows.append(row)
    return html.Div(rows, style={'maxHeight': '300px', 'overflowY': 'auto', 'overflowX': 'hidden', 'border': '1px solid #dddddd', 'padding': '10px'})
