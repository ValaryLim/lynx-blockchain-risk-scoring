import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
from datetime import datetime

app = dash.Dash(__name__, external_stylesheets=["assets/datepicker.css", dbc.themes.BOOTSTRAP])

#### STYLES ###################################################################
# style arguments for the sidebar
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "28rem",
    "padding": "2rem 1rem",
    "background-color": "#f1f4f9",
    "font-size": "15px"
}

# styles for the main content position it to the right of the sidebar with padding
CONTENT_STYLE = {
    "margin-left": "30rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

#### SIDEBAR ##################################################################
# entity input
entity_input = html.Div([
    dbc.Label("Entity Name", className="p", style={"font-weight": "600"}),
    dbc.Input(id="entity-input", placeholder="Type entity name here", \
        type="text", bs_size="md", className="mb-3", \
            style={"font-size": "14px"})
])

model_input = html.Div([
    dbc.Label("Model", className="p", style={"font-weight": "600"}),
    dbc.RadioItems(
        options=[
            {"label": "BERT", "value": 1},
            {"label": "FastText", "value": 2},
            {"label": "Word-2-Vec", "value": 3},
            {"label": "Vader", "value": 4},
        ],
        id="model-input", value=1, inline=True,
        style={"font-size": "14px"})
], style={"font-size": "14px"})

date_input = html.Div([
    dbc.Label("Date Range", className="p", style={"font-weight": "600"}),
    html.Br(),
    dcc.DatePickerRange(
        id="date-input",
        style={"font-size": "10px"},
        max_date_allowed = datetime.today(),
        initial_visible_month = datetime.today()
    )
])
# submit button
submit_button = dbc.Button("Submit", color="dark", block=True, id="submit")

sidebar = html.Div(
    [
        html.P("Lynx Demo", className="display-4"),
        html.H6("Demonstration Dashboard for BT4103", className="lead"),
        html.Hr(),
        entity_input,
        model_input,
        html.Br(),
        date_input,
        html.Br(),
        submit_button
    ],
    style=SIDEBAR_STYLE,
)

#### CONTENT ##################################################################
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
])

# table for conventional news

content = html.Div([html.P("hello")], id="page-content", style=CONTENT_STYLE)

#### LAYOUT ###################################################################

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

#### CALLBACKS ################################################################
# when submit button is pressed, run query
@app.callback(
    Output("page-content", "children"), 
    [Input("submit", "n_clicks")],
    [State("entity-input", "value"), 
    State("model-input", "value"), 
    State("date-input", "start_date"),
    State("date-input", "end_date")]
)
def render_page_content(entity, model, start_date, end_date, n_clicks):
    if n_clicks == None:
        return None
    return html.Div([
        html.P(entity),
        html.P(str(model)),
        html.P(start_date),
        html.P(str(type(start_date))),
        html.P(end_date),
        html.P(n_clicks)
    ])

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')