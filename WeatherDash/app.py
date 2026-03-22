import dash
from dash import dcc, html
from dash_extensions import WebSocket
from graph import graph_layout, register_graph_callbacks
from editor import editor_layout, register_editor_callbacks, IVAN_WS_URL
from graph import graph_layout, register_graph_callbacks, WEBSOCKET_URL

app = dash.Dash(__name__)

app.layout = html.Div([
    WebSocket(id='ws', url=WEBSOCKET_URL),
    WebSocket(id='ws-ivan', url=IVAN_WS_URL),
    dcc.Tabs([
        dcc.Tab(label='График', children=[graph_layout]),
        dcc.Tab(label='Редактор скриптов', children=[editor_layout]),
    ])
])

register_graph_callbacks(app)
register_editor_callbacks(app)

if __name__ == '__main__':
    app.run(debug=True,  use_reloader=False)