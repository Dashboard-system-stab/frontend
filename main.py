import dash
import os
from dash import dcc, html
from dash_extensions import WebSocket
from graph import graph_layout, register_graph_callbacks
from editor import editor_layout, register_editor_callbacks



app = dash.Dash(__name__)

WEBSOCKET_URL = os.environ.get("WEBSOCKET_URL", "ws://localhost:8765")
WEBSOCKET_SCRIPTS_URL = os.environ.get("WEBSOCKET_SCRIPTS_URL", "ws://localhost:7777")

app.layout = html.Div([
    
    WebSocket(id='ws', url=WEBSOCKET_URL),
    WebSocket(id='ws-ivan', url=WEBSOCKET_SCRIPTS_URL),
    dcc.Tabs([
        dcc.Tab(label='График', children=[graph_layout]),
        dcc.Tab(label='Редактор скриптов', children=[editor_layout]),
    ])
])

register_graph_callbacks(app)
register_editor_callbacks(app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050, debug=True, use_reloader=False)