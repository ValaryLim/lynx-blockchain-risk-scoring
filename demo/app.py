# import packages
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State
import plotly.express as px

import pandas as pd
from datetime import datetime

# set application
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
    "font-size": "12px"
}

# styles for the score displays
SCORE_STYLE = {
    "font-size": "15px", 
    "font-weight": "600", 
    "background-color": "#f1f4f9", 
    "height": "80px", 
    "border-radius": "25px", 
    "text-align": "center"

}

#### SIDEBAR ##################################################################
sidebar = html.Div(
    [
        html.P("Lynx Demo", className="display-4"),
        html.H6("Demonstration Dashboard for BT4103", className="lead"),
        html.Hr(),
    ],
    style=SIDEBAR_STYLE,
)

#### CONTENT ##################################################################
# entity input
'''
entity_input = html.Div([
    dbc.Label("Entity Name", className="p", style={"font-weight": "600"}),
    html.Br(),
    dbc.Input(id="entity-input", placeholder="Type entity name here", \
        type="text", bs_size="md", className="mb-3", \
            style={"font-size": "14px"})
], style={'width': '20%', 'display': 'inline-block', 'margin-right': 250})
'''
# retrieve entity list
entity_list = list(pd.read_csv('../sentiment-analysis/data/entity_list.csv').entity)
entity_list.sort() # sort in alphabetical order

entity_input = html.Div([
    dbc.Label("Entity Name", className="p", style={"font-weight": "600"}),
    html.Br(),
    dcc.Dropdown(
        id='entity-input',
        placeholder="Select entity name here", 
        options=[
            {'label': entity, 'value': entity} for entity in entity_list
        ],
        style={"font-size": "14px"}, 
        className="mb-3"
    ),
    html.Div(id='dd-output-container')
], style={'width': '40%', 'display': 'inline-block', 'margin-right': 100})

# date input
date_input = html.Div([
    dbc.Label("Date Range", className="p", style={"font-weight": "600"}),
    html.Br(),
    dcc.DatePickerRange(
        id="date-input",
        style={"font-size": "10px"},
        min_date_allowed = '2020-01-01',
        max_date_allowed = datetime.today(),
        initial_visible_month = datetime.today()
    )
], style={'width': '40%', 'display': 'inline-block', 'margin-right': 100})

# submit button
submit_button = dbc.Button("Submit", color="dark", block=True, id="submit", style={'width': '10%', 'display': 'inline-block'})

content = html.Div(
    [

        entity_input,
        date_input,
        submit_button,
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
    id="page-content", style=CONTENT_STYLE,
)

#### LAYOUT ###################################################################

app.layout = html.Div([dcc.Location(id="url"), sidebar, \
    dbc.Spinner(content, spinner_style={"width": "3rem", "height": "3rem"})])

#### CALLBACKS ################################################################
def generate_table(name, dataframe, max_rows=10):
    '''
    generate table dynamically from dataframe
    '''
    return html.Div([html.H5(name),
        dbc.Label(f"Total Articles Retrieved: {len(dataframe)}", 
                    style={"font-weight": "600", "font-size": "14px"}),
        dbc.Table([
            html.Thead(
                html.Tr([html.Th(col) for col in dataframe.columns])
            ),
            html.Tbody([
                html.Tr([
                    html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
                ]) for i in range(min(len(dataframe), max_rows))
            ])
        ])
    ])

def generate_table_updated(name, dataframe):
    return html.Div([html.Br(),
        html.H5(name),
        dbc.Label(f"Total Articles Retrieved: {len(dataframe)}", 
                    style={"font-weight": "600", "font-size": "14px"}),
        html.Br(),
        html.Div(
            dash_table.DataTable(
                id='articles-table',
                columns=[
                    {"name": i, "id": i, "selectable":False} for i in dataframe.columns
                ],
                data=dataframe.to_dict('records'),
                style_table={'overflowX': 'auto'},
                style_cell={
                    'height': 'auto',
                    # all three widths are needed
                    'minWidth': '80px', 'width': '150px', 'maxWidth': '180px',
                    'whiteSpace': 'normal',
                    'textAlign': 'left',
                    'fontSize': 12, 
                    'font-family':'Verdana',
                },
                sort_action='native',
                sort_mode='single',
                sort_by=[]
            ), 
            style={'width': '100%', 'display': 'inline-block'})
])


def generate_graph(crypto_df, reddit_df, twitter_df, entity, start_date, end_date):

    # df1 = get_count_by_date(crypto_df, start_date, end_date)
    # df2 = get_count_by_date(reddit_df, start_date, end_date)
    # df3 = get_count_by_date(twitter_df, start_date, end_date)

    # get risk score by source
    df1 = get_risk_score_by_date(crypto_df, start_date, end_date)
    df2 = get_risk_score_by_date(reddit_df, start_date, end_date)
    df3 = get_risk_score_by_date(twitter_df, start_date, end_date)

    df1['source_type'] = 'News'
    df2['source_type'] = 'Reddit'
    df3['source_type'] = 'Twitter'

    result = pd.concat([df1, df2], ignore_index=True, sort=False)
    result = pd.concat([result, df3], ignore_index=True, sort=False)
    result['date'] = result['index'].dt.date

    # fig = px.line(result, x= 'index', y='label', color='source_type')
    fig = px.line(result, x='index', y='probability_risk', color='source_type')
    
    # get overall risk score
    sample_risk_data = pd.read_csv("sample_risk_data.csv")

    fig.update_layout(
        # title="Number of posts/articles labelled high-risk over time",
        title_x=0.5,
        xaxis_title="Date",
        yaxis_title="Risk Score (in %)",
        legend_title="Source"
    )
    
    count_graph = html.Div([
        html.H5("Risk Score over Time"),
        dcc.Graph(figure=fig)
    ]
    )
    
    return count_graph

def get_risk_score_by_date(df, start_date, end_date):
    # Group data by date and find the number of posts predicted as risky 
    df2 = df.groupby(['date'])['probability_risk'].mean()
    df = df.drop(['date'], axis = 1)

    # Get all date within range and fill dates with no data with 0 
    idx = pd.date_range(start_date, end_date)
    df2.index =  pd.DatetimeIndex(df2.index)
    df2 = df2.reindex(idx, fill_value=0) 

    df2 = df2.reset_index()
    return df2

'''
def get_count_by_date(df, start_date, end_date):

    #Group data by date and find the number of posts predicted as risky 
    df2 = df.groupby(['date']).sum()
    df = df.drop(['date'], axis = 1)

    #Get all date within range and fill dates with no data with 0 
    idx = pd.date_range(start_date, end_date)
    df2.index =  pd.DatetimeIndex(df2.index)
    df2 = df2.reindex(idx, fill_value=0) 

    df2 = df2.reset_index()
    return df2
'''

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

def render_page_content(n_clicks, entity, start_date, end_date):
    if n_clicks == None:
        return (None, None, None, None, None)

    # convert start and end date to datetime
    start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    end_date_datetime = end_date_datetime.replace(hour=23, minute=59)

    # generate score display
    score_display = html.Div([
        dbc.Label("Open Source Information", className="p", style={"font-size": "30px", "font-weight": "600", 'display': 'inline-block', 'margin-right': 50}),
        dbc.Col(html.Div("Overall score"), style={"font-size": "15px", "font-weight": "600", 'width': '10%', 'display': 'inline-block', "background-color": "#D77560", "height": "30px", "border-radius": "25px", "text-align": "center"}),
        html.Br(),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(html.Div("News", style=SCORE_STYLE)),
                dbc.Col(html.Div("Reddit", style=SCORE_STYLE)),
                dbc.Col(html.Div("Twitter", style=SCORE_STYLE)),
            ]
        ),   
    ]
    )

    # generate graph
    count_graph = html.Div([
        html.H5("Count of Risky Articles over Time")]
    )
    sample_data = pd.read_csv("sample_data.csv", index_col=0)
    
    # Process imported dataframe
    # Get datetime format for df date and filter for range
    sample_data['article_date'] = pd.to_datetime(sample_data.article_date)
    
    # Filter by entity and date range
    df = sample_data.copy()
    df['entity'] = df['entity'].str.lower()
    df = df.loc[df['entity'] == entity.lower()]
    df = df.loc[(df['article_date'] >= start_date) & (df['article_date'] <= end_date)]
    
    df['label'] = df['probability_risk'].apply(lambda x: 1 if x >= 0.5 else 0)
    
    # Format 
    df['date'] = df['article_date'].dt.date
    df = df.round({'predicted_risk': 2})
    crypto_df = df[(df.source!="twitter") & (df.source!="reddit")]
    reddit_df = df.loc[df['source']=="reddit"]
    twitter_df = df.loc[df['source']=="twitter"]

    count_graph = generate_graph(crypto_df, reddit_df, twitter_df, entity, str(start_date),str(end_date))


    # rename columns
    columns = {"date": "Date", "content": "Content", \
                "url": "URL", "predicted_risk": "Risk Score"}
    
    # slice dataframe
    crypto_df = pd.DataFrame(crypto_df[columns.keys()].sort_values("predicted_risk", ascending = False))
    reddit_df = pd.DataFrame(reddit_df[columns.keys()].sort_values("predicted_risk", ascending = False))
    twitter_df = pd.DataFrame(twitter_df[columns.keys()].sort_values("predicted_risk", ascending = False))

    # tables
    # crypto_table = generate_table("Conventional and Cryptonews", crypto_df.rename(columns=columns))
    # reddit_table = generate_table("Reddit", reddit_df.rename(columns=columns))
    # twitter_table = generate_table("Twitter", twitter_df.rename(columns=columns))
    crypto_table = generate_table_updated("Conventional and Cryptonews", crypto_df.rename(columns=columns))
    reddit_table = generate_table_updated("Reddit", reddit_df.rename(columns=columns))
    twitter_table = generate_table_updated("Twitter", twitter_df.rename(columns=columns))

    return (score_display, count_graph, crypto_table, reddit_table, twitter_table)

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')