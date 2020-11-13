# import packages
import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

import pandas as pd
from datetime import datetime, timedelta
import base64

# set application
app = dash.Dash(__name__, suppress_callback_exceptions=True, \
                external_stylesheets=["assets/datepicker.css", dbc.themes.BOOTSTRAP])
server = app.server


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
    "font-size": "12px"
}

# styles for the score displays
SCORE_STYLE = {
    "font-size": "16px", 
    "font-weight": "600", 
    "background-color": "#f1f4f9", 
    "border-color": "white",
    "display": "inline-block",
    "width": "30px",
    # "height": "65px", 
    "border-radius": "100px", 
    "padding": "10px",
    "text-align": "center",
    "vertical-align": "center",
}

# styles for the side tabs
TAB_STYLE = {
    "font-size": "20px", 
    "font-weight": "600", 
    "text-align": "left"
}

unclicked_button_style = {'background-color': '#f1f4f9',
                            'border': '#f1f4f9',
                            'color': 'black',
                            'height': '70px',
                            'width': '100%',
                            'margin-top': '0px',
                            'margin-left': '0px'}

clicked_button_style = {'background-color': 'white',
                        'border': '#f1f4f9',
                        'color': 'darkblue',
                        'height': '70px',
                        'width': '100%',
                        'margin-top': '0px',
                        'margin-left': '0px'}


#### SIDEBAR ##################################################################
# image
image_filename = 'assets/lynx_logo.png'
encoded_image = base64.b64encode(open(image_filename, 'rb').read())

sidebar = html.Div(
    [
        html.Img(src='https://s2-cdn.greenhouse.io/external_greenhouse_job_boards/logos/400/688/200/original/Lynx_LinkedIn.png?1573727274', style={'width': '300px', 'height': '50px', 'object-fit': 'cover'}),
        html.H5("CyLynx Demo", className="display-4", style={'font-weight': '500'}),
        html.H6("Demonstration Dashboard for BT4103", className="lead"),
        html.Hr(),
        html.Br(),
        # dcc.Link(html.H6('Overall Demonstration', style=TAB_STYLE), href='overall'),
        dcc.Link(
            html.Button(html.H6("Overall Demonstration", style=TAB_STYLE), id='overall-button',
                n_clicks=0,
                style=unclicked_button_style), href='overall'
        ),
        html.Br(),
        dcc.Link(
            html.Button(html.H6("Entity Demonstration", style=TAB_STYLE), id='entity-button',
            n_clicks=0,
            style=unclicked_button_style), href='entity'
        ),
    ],
    style=SIDEBAR_STYLE,
)


#### ENTITY PAGE CONTENT ##################################################################
# retrieve entity list
entity_list = list(pd.read_csv('https://raw.githubusercontent.com/ValaryLim/lynx-blockchain-risk-scoring/yanjean/dashboard/demo/data/entity_list.csv', sep=',').entity)
entity_list.sort() # sort in alphabetical order

# entity input
entity_input = html.Div([
    dbc.Label("Entity Name", className="p", style={"font-weight": "600", "font-size": "14px"}),
    html.Br(),
    dcc.Dropdown(
        id='entity-input',
        placeholder="Select entity name here", 
        options=[
            {'label': entity, 'value': entity} for entity in entity_list
        ],
        style={"font-size": "14px"}, 
        className="mb-3",
    ),
    html.Div(id='dd-output-container')
], style={'width': '30%', 'display': 'inline-block', 'margin-right': 30})

# read sample_risk_data
sample_risk_data = pd.read_csv('https://raw.githubusercontent.com/ValaryLim/lynx-blockchain-risk-scoring/yanjean/dashboard/demo/data/entity_risk_score_data.csv', sep=',')
sample_risk_data['date_format'] = sample_risk_data.apply(lambda x: x.date[0:10], axis=1)
max_date = max(sample_risk_data['date_format'])
max_date = datetime.strptime(max_date, '%Y-%m-%d') + timedelta(days=1)

# date input
date_input = html.Div([
    dbc.Label("Date Range", className="p", style={"font-weight": "600", "font-size": "14px"}),
    html.Br(),
    dcc.DatePickerRange(
        id="date-input",
        style={"font-size": "14px"},
        min_date_allowed = min(sample_risk_data['date']),
        max_date_allowed =  max_date,
        initial_visible_month = datetime.today(),
        className="mb-3"
    )
], style={'width': '40%', 'display': 'inline-block', 'margin-right': 20})

# submit button
submit_button = html.Div([
    dbc.Label("Button", className="p", style={"color": "white", "font-weight": "600"}), # for alignment
    html.Br(),
    dbc.Button("Submit", color="dark", block=False, id="submit", className="mb-3")
], style={'width': '20', 'display': 'inline-block'})

# entity page layout
entity_content = html.Div(
    [
        dbc.Row([entity_input, date_input, submit_button]),
        html.Hr(),
        html.Br(),
        html.Br(),
        html.Div(id = "score-display"),
        html.Br(),
        html.Br(),
        html.Div(id = "count-graph"),
        html.Div(id="conventional-news"),
        html.Div(id="reddit-news"),
        html.Div(id="twitter-news"),
        
    ], 
    id="entity-page-content", style=CONTENT_STYLE,
)


#### APP LAYOUT ###################################################################
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    sidebar,
    html.Div(id='page-content')
    # dbc.Spinner(id='page-content', spinner_style={"width": "3rem", "height": "3rem"})
])


#### ENTITY PAGE CALLBACKS ################################################################

def generate_table(name, dataframe):
    '''
    generate table dynamically from dataframe
    '''
    return html.Div([
        html.Br(),
        html.H5(name),
        dbc.Label(f"Total Articles Retrieved: {len(dataframe)}", 
                    style={"font-weight": "600", "font-size": "14px"}),
        html.Br(),
        html.Div(
            dash_table.DataTable(
                columns=[
                    {"name": i, "id": i, "selectable":True} for i in dataframe.columns
                ],
                data=dataframe.to_dict('records'),
                style_data={'whiteSpace': 'normal'},
                style_header={'fontWeight': 'bold'},
                style_cell={
                    # all three widths are needed
                    'minWidth': '5px', 'width': '80px', 'maxWidth': '180px',
                    'minHeight': '10px', 'height': '10px', 'maxHeight': '10px',
                    'whiteSpace': 'normal',
                    'fontSize': 12,
                    'font-family': 'Verdana',
                    'overflow': 'hidden',
                },
                style_cell_conditional = [
                                          {'if': {'column_id': 'Date'}, 'textAlign': 'center'},
                                          {'if': {'column_id': 'Risk Score'}, 'textAlign': 'center'},
                                          {'if': {'column_id': 'Content'}, 'textAlign': 'left'},
                                          {'if': {'column_id': 'URL'}, 'textAlign': 'left'}],
                sort_action='native',
                sort_mode='single',
                sort_by=[],
                page_size=5,
                css=[{'selector': '.row', 'rule': 'margin: 0'}],
                
            style_as_list_view=True,
            ), 
            style={}),
        html.Br(),
        html.Br()
])

def generate_graph(entity, start_date, end_date):
    '''
    generate graph of risk score over time for each entity
    with breakdown by news source
    '''

    # read csv of risk data
    sample_risk_data = pd.read_csv('https://raw.githubusercontent.com/ValaryLim/lynx-blockchain-risk-scoring/yanjean/dashboard/demo/data/entity_risk_score_data.csv', sep=',')
    # extract relevant date and entity
    sample_risk_data = sample_risk_data.loc[sample_risk_data['entity']==entity.lower()]
    sample_risk_data = sample_risk_data[(sample_risk_data.date >= start_date) & (sample_risk_data.date <= end_date)]

    # transform data
    graph_data = pd.DataFrame(columns=['date', 'score', 'source'])

    for col in ['news_score', 'reddit_score', 'twitter_score', 'score']:
        source_data = sample_risk_data[['date', col]]
        if col == 'score':
            source_data['source'] = 'overall'
        else:
            source_data['source'] = col
        source_data.columns=['date', 'score', 'source']
        graph_data = graph_data.append(source_data, ignore_index=True)

    # plot graph
    fig = px.line(graph_data, x='date', y='score', color='source', \
                  line_dash_sequence=['dot', 'dot', 'dot', 'solid'],
                  line_dash='source', \
                  color_discrete_sequence=['#0CC078', '#FB6962', '#6EB5FF', 'black'])

    fig.update_layout(
        # title="Risk Score Over Time",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Risk Score",
        legend_title="Source",
    )

    count_graph = html.Div([
        html.H5("Risk Score over Time"),
        dcc.Graph(figure=fig)
    ]
    )

    return count_graph

# when submit button is pressed, run query
@app.callback(
    [Output("score-display", "children"),
    Output("count-graph", "children"),
    Output("conventional-news", "children"),
    Output("reddit-news", "children"),
    Output("twitter-news", "children")],
    [Input("submit", "n_clicks")],
    [State("entity-input", "value"), 
    State("date-input", "start_date"),
    State("date-input", "end_date")
    ]
)

def render_entity_page(n_clicks, entity, start_date, end_date):
    if n_clicks == None:
        return (None, None, None, None, None)

    # convert start and end date to datetime
    start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    end_date_datetime = end_date_datetime.replace(hour=23, minute=59)

    ##### SCORE DISPLAY #####
    # read csv of risk data
    sample_risk_data = pd.read_csv('https://raw.githubusercontent.com/ValaryLim/lynx-blockchain-risk-scoring/yanjean/dashboard/demo/data/entity_risk_score_data.csv', sep=',')
    # extract relevant date and entity
    sample_risk_data = sample_risk_data.loc[sample_risk_data['entity']==entity.lower()]
    sample_risk_data = sample_risk_data[(sample_risk_data.date >= start_date) & (sample_risk_data.date <= end_date)]
    # max score over time
    max_score = pd.DataFrame(sample_risk_data.max(axis=0)).iloc[1:5]
    max_score.columns = ['max_score']
    max_score['max_score'] = [round(float(x), 2) for x in max_score['max_score']]

    def get_color(score):
        if score >= 75:
            return 'red'
        elif score >= 50:
            return '#FF8C00' # orange
        else:
            return 'black'

    score_display = html.Div([
        dbc.Label("Open Source Information", className="p", style={"font-size": "30px", "font-weight": "600", 'display': 'inline-block', 'margin-right': 50}),
        dbc.Label((f"Overall Score: {str(max_score.loc['score', 'max_score'])}"), 
                    className="p", style={"color": get_color(max_score.loc['score', 'max_score']), "font-size": "20px", "font-weight": "600", 'width': '300px', 'display': 'inline-block', "background-color": "#f1f4f9", "height": "40px", "padding": "5px", "text-align": "center", "vertical-align": "center"}),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col([
                    html.Div("News"),
                    html.Div(str(max_score.loc['news_score', 'max_score']), 
                    style={'color': get_color(max_score.loc['news_score', 'max_score'])})],
                    style=SCORE_STYLE),

                dbc.Col([
                    html.Div("Reddit"),
                    html.Div(str(max_score.loc['reddit_score', 'max_score']), 
                    style={'color': get_color(max_score.loc['reddit_score', 'max_score'])})],
                    style=SCORE_STYLE),

                dbc.Col([
                    html.Div("Twitter"),
                    html.Div(str(max_score.loc['twitter_score', 'max_score']), 
                    style={'color': get_color(max_score.loc['twitter_score', 'max_score'])})],
                    style=SCORE_STYLE),
            ]
        ),  
        html.Br(),

        dbc.Row([
            html.Div("Legend:  ", style={"font-size": '16px', "font-weight": 400, 'display': 'inline-block', "padding": "10px"}), 
            html.Div("High Risk  ", style={"font-size": '16px', "font-weight": 400, 'color':'red', 'display': 'inline-block', "padding": "10px"}),
            html.Div("Medium Risk  ", style={"font-size": '16px', "font-weight": 400, 'color': '#FF8C00', 'display': 'inline-block', "padding": "10px"}),
            html.Div("Low/ No Risk ", style={"font-size": '16px', "font-weight": 400, 'display': 'inline-block', "padding": "10px"})]),

        html.Br(), 
    ]
    )

    ##### GRAPH #####
    count_graph = html.Div(generate_graph(entity, str(start_date),str(end_date)))

    ##### TABLE #####
    sample_data = pd.read_csv('https://raw.githubusercontent.com/ValaryLim/lynx-blockchain-risk-scoring/yanjean/dashboard/demo/data/post_data.csv', sep=',', index_col=0)
    
    # Process imported dataframe
    # Get datetime format for df date and filter for range
    sample_data['article_date'] = pd.to_datetime(sample_data.article_date)
    
    # Filter by entity and date range
    df = sample_data.copy()
    df['entity'] = df['entity'].str.lower()
    df = df.loc[df['entity'] == entity.lower()]
    df = df.loc[(df['article_date'] >= start_date_datetime) & (df['article_date'] <= end_date_datetime)]    
    
    # format data
    df['date'] = df['article_date'].dt.date
    df = df.round({'predicted_risk': 2})
    crypto_df = df[(df.source!="twitter") & (df.source!="reddit")]
    reddit_df = df[df.source=="reddit"]
    twitter_df = df[df.source=="twitter"]

    # rename columns
    columns = {"date": "Date", "content": "Content", \
                "url": "URL", "predicted_risk": "Risk Score"}

    # slice dataframe to retrieve relevant information to display
    crypto_df = pd.DataFrame(crypto_df[columns.keys()].sort_values("predicted_risk", ascending = False))
    reddit_df = pd.DataFrame(reddit_df[columns.keys()].sort_values("predicted_risk", ascending = False))
    twitter_df = pd.DataFrame(twitter_df[columns.keys()].sort_values("predicted_risk", ascending = False))

    # generate tables
    crypto_table = generate_table("Conventional and Cryptonews", crypto_df.rename(columns=columns))
    reddit_table = generate_table("Reddit", reddit_df.rename(columns=columns))
    twitter_table = generate_table("Twitter", twitter_df.rename(columns=columns))

    return (score_display, count_graph, crypto_table, reddit_table, twitter_table)


#### OVERALL PAGE CONTENT ##################################################################

overall_content = html.Div(
    [
        dbc.Row([date_input, submit_button]),
        html.Hr(),
        # html.Br(),
        # html.Br(),
        # html.Div(id = "overall-score-display"),
        # html.Br(),
        html.Br(),
        html.Div(id='overall-graph'),
        html.Div(id='overall-table')
    ], 
    id="overall-page-content", style=CONTENT_STYLE,
)

#### OVERALL PAGE CALLBACKS ################################################################
def generate_overall_table(name, dataframe):
    '''
    generate table dynamically from dataframe
    '''
    return html.Div([
        html.Br(),
        html.H5(name),
        html.Br(),
        html.Div(
            dash_table.DataTable(
                columns=[
                    {"name": i, "id": i, "selectable":False} for i in dataframe.columns
                ],
                data=dataframe.to_dict('records'),
                page_action='none',
                fixed_rows={'headers': True},
                style_table={'height': '300px', 'overflowY': 'auto', 'width': '600px'},
                style_header={'fontWeight': 'bold'},
                style_data={'whiteSpace': 'normal', 'height': 'auto'},
                style_cell={
                    'height': 'auto',
                    # all three widths are needed
                    # 'minWidth': '30px', 'width': '50px', 'maxWidth': '80px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left',
                    'fontSize': 12, 
                    'font-family':'Verdana',
                },
                css=[{'selector': '.row', 'rule': 'margin: 0'}],
            ), 
            style={})
])

@app.callback(
    [Output("overall-graph", "children"),
    Output("overall-table", "children")],
    [Input("submit", "n_clicks")],
    [State("date-input", "start_date"),
    State("date-input", "end_date")
    ]
)

def render_overall_page(n_clicks, start_date, end_date):
    if n_clicks == None:
        # return (None, None, None)
        return (None, None)

    ##### SCORE DISPLAY #####
    # read csv of risk data
    sample_risk_data = pd.read_csv('https://raw.githubusercontent.com/ValaryLim/lynx-blockchain-risk-scoring/yanjean/dashboard/demo/data/entity_risk_score_data.csv', sep=',')
    # extract relevant date and entity
    sample_risk_data = sample_risk_data[(sample_risk_data.date >= start_date) & (sample_risk_data.date <= end_date)]

    ##### GRAPH #####
    overall_graph = html.Div(generate_graph('overall', str(start_date),str(end_date)))

    ##### TABLE #####
    # create overall data
    overall_data = sample_risk_data.loc[sample_risk_data['entity'] != 'overall']
    # extract relevant columns to display
    overall_data = overall_data[['date', 'entity', 'score']]
    overall_data = overall_data.round({'score': 2})
    # sort by score
    overall_data = overall_data.sort_values(by=['score'], ascending=False)
    # rename columns
    overall_data = overall_data.rename(columns={"date": "Date", "score": "Score", "entity": "Entity"})

    overall_table = generate_overall_table("High Risk Entities by Overall Score", overall_data)

    return (overall_graph, overall_table)


#### RENDER PAGE CONTENT ################################################################

# Update the index
@app.callback(
    [
    Output('overall-button', 'style'),
    Output('entity-button', 'style'),
    Output('page-content', 'children')],
    Input('url', 'pathname')
)

def render_page_content(pathname):
    if pathname == '/entity':
        return (unclicked_button_style, clicked_button_style, entity_content)

    else: # the default is always the overall
        return (clicked_button_style, unclicked_button_style, overall_content)

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')
