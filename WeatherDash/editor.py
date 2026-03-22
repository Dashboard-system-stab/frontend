# editor.py
import json
from dash import dcc, html, no_update, ctx
from dash.dependencies import Output, Input, State
from styles import BUTTON_STYLE, PANEL_STYLE

IVAN_WS_URL = "ws://localhost:7777"

# ---------- Лейаут ----------
editor_layout = html.Div([

    html.Div([

        # Верхняя панель — список файлов и кнопки
        html.Div([
            dcc.Dropdown(
                id='script-dropdown',
                placeholder='Нажмите Открыть',
                options=[],
                style={'width': '300px', 'display': 'inline-block', 'verticalAlign': 'middle'}
            ),
            html.Button('Открыть', id='btn-open', n_clicks=0, style={**BUTTON_STYLE, 'width': 'auto', 'marginLeft': '10px', 'padding': '6px 16px'}, type='button'),
            html.Button('Сохранить', id='btn-save', n_clicks=0, style={**BUTTON_STYLE, 'width': 'auto', 'marginLeft': '10px', 'padding': '6px 16px'}, type='button'),
            html.Div(id='editor-status', style={'display': 'inline-block', 'marginLeft': '15px', 'fontSize': '13px', 'color': 'green'}),
        ], style={'marginBottom': '12px'}),

        # Текстовое поле редактора
        dcc.Textarea(
            id='script-editor',
            placeholder='Выберите файл и нажмите Открыть...',
            style={
                'width': '100%',
                'height': '400px',
                'fontFamily': 'Courier New, monospace',
                'fontSize': '13px',
                'padding': '10px',
                'border': '1px solid #dddddd',
                'borderRadius': '4px',
                'boxSizing': 'border-box',
                'resize': 'vertical',
            }
        ),

    ], style={**PANEL_STYLE, 'marginTop': '20px'}),

])


# ---------- Колбэки ----------
def register_editor_callbacks(app):

    # Отправка запросов Ивану
    @app.callback(
        Output('ws-ivan', 'send'),
        Input('btn-open', 'n_clicks'),
        Input('btn-save', 'n_clicks'),
        Input('script-dropdown', 'value'),
        State('script-editor', 'value'),
        State('script-dropdown', 'value'),
        prevent_initial_call=True
    )
    def handle_ivan_send(btn_open, btn_save, dropdown_value, editor_content, filename):
        triggered = ctx.triggered_id

        if triggered == 'btn-open':
            return json.dumps({'type': 'get_list'})

        if triggered == 'script-dropdown' and dropdown_value:
            return json.dumps({'type': 'get_file', 'filename': dropdown_value})

        if triggered == 'btn-save':
            if not filename or not editor_content:
                return no_update
            return json.dumps({'type': 'save_file', 'filename': filename, 'content': editor_content})

        return no_update

    # Приём ответов от Ивана
    @app.callback(
        Output('script-dropdown', 'options'),
        Output('script-editor', 'value'),
        Output('editor-status', 'children'),
        Input('ws-ivan', 'message'),
        prevent_initial_call=True
    )
    def receive_from_ivan(message):
        if message is None:
            return no_update, no_update, no_update
        try:
            data = json.loads(message['data'])

            if 'files' in data:
                options = [{'label': f, 'value': f} for f in data['files']]
                return options, no_update, ''

            if 'content' in data:
                return no_update, data['content'], ''

            if data.get('status') == 'ok':
                return no_update, no_update, 'Успешно сохранено'

        except (json.JSONDecodeError, KeyError, TypeError):
            return no_update, no_update, 'Ошибка ответа от сервера'

        return no_update, no_update, no_update