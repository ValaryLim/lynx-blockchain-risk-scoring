# import packages
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
from datetime import datetime

# data
import sys
sys.path.insert(1, '../scraping')
from main_conventional import conventional_scrape_by_entity
from main_crypto import crypto_scrape_by_entity
from reddit import reddit_scrape_byentity

# data processing
import string 
import nltk
from nltk.stem import WordNetLemmatizer # word lemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords # stopwords

# models
import fasttext
sys.path.insert(1, '../sentiment-analysis')
from vader import vader_predict

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
            {"label": "BERT", "value": "bert"},
            {"label": "FastText", "value": "fasttext"},
            {"label": "Word-2-Vec", "value": "wordvec"},
            {"label": "Vader", "value": "vader"},
        ],
        id="model-input", value="bert", inline=True,
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
content = html.Div([
    html.Div(id="conventional-news"),
    html.Div(id="reddit-news"),
    html.Div(id="twitter-news"),
], id="page-content", style=CONTENT_STYLE)

#### LAYOUT ###################################################################

app.layout = html.Div([dcc.Location(id="url"), sidebar, \
    dbc.Spinner(content, spinner_style={"width": "3rem", "height": "3rem"})])

#### CALLBACKS ################################################################
def generate_table(name, dataframe, max_rows=10):
    '''
    generate table dynamically from dataframe
    '''
    return html.Div([html.H5(name),
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

def pre_processing(text, lemmatize=True, stem=False):
    '''
    Preprocessing for fasttext model
    '''
    # strip accents
    text = text.encode('ascii', 'ignore')
    text = str(text.decode("utf-8"))

    # covert to lowercase
    text = text.lower()

    # remove punctuation
    text = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))

    # remove unnecessary white spaces
    text = text.replace("\n", "")

    # tokenize
    text_words = nltk.word_tokenize(text)

    # lemmatize
    if lemmatize:
        wordnet_lemmatizer = WordNetLemmatizer()
        text_words = [wordnet_lemmatizer.lemmatize(x, pos="v") for x in text_words]

    # stem
    if stem:
        stemmer = SnowballStemmer("english")
        text_words = [stemmer.stem(x) for x in text_words]

    # remove stop words
    stop = list(stopwords.words('english'))
    keep_stopwords = ["no", "not", "nor"]
    for word in keep_stopwords:
        stop.remove(word)
        stop = set(stop)
    text_words = [x for x in text_words if not x in stop]

    return ' '.join(text_words)

# when submit button is pressed, run query
@app.callback(
    [Output("conventional-news", "children"),
    Output("reddit-news", "children"),
    Output("twitter-news", "children")], 
    [Input("submit", "n_clicks")],
    [State("entity-input", "value"), 
    State("model-input", "value"), 
    State("date-input", "start_date"),
    State("date-input", "end_date")]
)
def render_page_content(n_clicks, entity, model, start_date, end_date):
    if n_clicks == None:
        return (None, None, None)

    # convert start and end date to datetime
    start_date_datetime = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_datetime = datetime.strptime(end_date, "%Y-%m-%d")
    end_date_datetime = end_date_datetime.replace(hour=23, minute=59)
    
    # retrieve data based on information
    crypto_df = conventional_scrape_by_entity(entity, start_date_datetime, end_date_datetime)
    crypto_df = pd.concat([crypto_df, crypto_scrape_by_entity(entity, start_date_datetime, end_date_datetime)])
    crypto_df["text"] = crypto_df["title"].fillna('') + " " + crypto_df["excerpt"].fillna('')
    
    reddit_df = reddit_scrape_byentity(entity, start_date_datetime, end_date_datetime)
    reddit_df["text"] = reddit_df["title"].fillna('') + " " + reddit_df["excerpt"].fillna('')

    # process text for modelling
    crypto_df["text_processed"] = crypto_df["text"].apply(lambda x: pre_processing(x, lemmatize=True, stem=False))
    reddit_df["text_processed"] = reddit_df["text"].apply(lambda x: pre_processing(x, lemmatize=True, stem=False))

    # load model
    if model == 'fasttext':
        model_fasttext = fasttext.load_model("../sentiment-analysis/models/fasttext/sample_all_lemmatize.bin")
        crypto_df["label"] = crypto_df["text_processed"].apply(lambda x: int(model_fasttext.predict(x)[0][0][-1]))
        reddit_df["label"] = reddit_df["text_processed"].apply(lambda x: int(model_fasttext.predict(x)[0][0][-1]))

    elif model == 'vader':
        crypto_df["label"] = crypto_df["text"].apply(lambda x: vader_predict(x))
        reddit_df["label"] = reddit_df["text"].apply(lambda x: vader_predict(x))

    # slice dataframe
    crypto_df = crypto_df[["date_time", "text", "label"]]
    reddit_df = reddit_df[["date_time", "text", "label"]]

    return (generate_table("Conventional and Cryptonews", crypto_df),  generate_table("Reddit", reddit_df), None)

if __name__ == "__main__":
    app.run_server(debug=True, host='127.0.0.1')