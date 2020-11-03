import pandas as pd
from datetime import datetime
from bitcoin import bitcoin_scrape
from bitcoinist import bitcoinist_scrape 
from bitnewstoday import bitnewstoday_scrape
from coindesk import coindesk_scrape
from cointelegraph import cointelegraph_scrape
from cryptonews import cryptonews_scrape 
from cryptoslate import cryptoslate_scrape 
from forbes import forbes_scrape
from insidebitcoins import insidebitcoins_scrape
from nulltx import nulltx_scrape

import string # for punctuation
import math
import nltk
from nltk.stem import WordNetLemmatizer 
from langdetect import detect

def filter_entity(sentence, entity):
    entity_list = str(entity).lower().split()
    sentence_list = str(sentence).lower().split()
    found = 0
    for entity_word in entity_list:
        if entity_word in sentence_list:
            found += 1
    return found == len(entity_list)

def filter_out(sentence):
    '''
    Output: True if sentence should be kept, False otherwise 
    '''
    # set of words to filter out (lemmatized)
    filter_set = {'price', 'rat', 'fee', 'liquidity', 'trade', 'trade', 'invest', 'value',\
        'update', 'winner', 'history', 'competition', 'review', 'welcome', 'bull', 'bear', \
        'perform', 'cost', 'discount', 'spend', 'perform', 'potential', 'interest', 'success',\
        'prediction', 'forecast', 'top', 'return', 'gift', 'demand', 'trend', 'shop', 'buy',\
        'brief', 'tip', 'complete', 'expand', 'improve', 'retail', 'explain', 'investment', \
        'sentiment', 'rewind', 'trader', 'trade', 'innovation', 'joke', 'tax', 'pros', 'rewind', \
        'hype', 'how', 'war', 'drop', 'falling', 'inflation', 'remedy', 'recover', 'introduction',\
        'investors', 'dip', 'legalize', 'regulate', 'launch', 'support', 'grant', 'arbitrage'}

    # if there exist no sentence (excerpt), return True
    if type(sentence) != str:
        if math.isnan(sentence):
            return True

    # pre-process sentence
    processed_sentence = pre_processing(sentence)

    for word in processed_sentence:
        if word in filter_set: 
            return False

    return True



def filter_in(sentence):
    '''
    Output: True if sentence should be kept, False otherwise 
    '''
    # set of words to filter out (lemmatized)
    filter_set = {'unsecure','insecure', 'secure', 'security', 'breach', 'hack', 'compromise',\
        'steal', 'fraud', 'scam', 'heist', 'attack', 'malware', 'suspicious', 'cryptojacking',\
        'launder', 'allegation','raid', 'emergency', 'suspect', 'risk', 'chaos', 'assault',\
        'theft', 'criticism','shutdown', 'down', 'disable', 'regulate', 'phish', 'illegal',\
        'fake', 'suspend','vulnerable', 'leak', 'fraudster'}

    # pre-process sentence
    processed_sentence = pre_processing(sentence)

    for word in processed_sentence:
        if word in filter_set: 
            return True
    
    return False


def pre_processing(sentence):
    wordnet_lemmatizer = WordNetLemmatizer()

    # covert to lowercase
    sentence = sentence.lower()

    # remove punctuation
    sentence = sentence.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))

    # split sentence
    sentence_words = nltk.word_tokenize(sentence)

    # lemmatize
    lemma_words = [wordnet_lemmatizer.lemmatize(x, pos="v") for x in sentence_words]
    
    return lemma_words

def process_duplicates(df):
    '''
    Accepts a pandas dataframe and outputs 
    '''
    if df.empty:
        df["count"] = 0
        df["date_time_first"] = ""
        return df
    
    # assign count based on text and entity
    df["count"] = df.groupby(by=["text", "entity"]).text.transform('size')

    # get array of all date times
    df = df.merge(df.groupby(['text', 'entity']).date_time.agg(list).reset_index(), 
              on=['text', 'entity'], 
              how='left',
                  suffixes=['', '_all'])
    
    # drop duplicates, keeping the first
    df = df.drop_duplicates(subset=["text", "entity"], keep='first')

    return df

def enTweet(sentence):
    '''
    Checks that tweet is in english
    '''
    try:
        language = detect(sentence)
        if(language == 'en'):
            return True
        else:
            return False
    except:
        print('exception!')
        return False
import re
import pandas as pd
import sys

def is_alphanumeric(text):
    return any(char.isdigit() for char in text) and any(char.isalpha() for char in text)

def get_coins(text):
    coin_lst = pd.read_csv('./coin_lst.csv')['coins'].str.lower().tolist()
    #coin_lst = pd.read_csv(r'./data/coin_lst.csv')['coins'].str.lower().tolist()
    coins = []

    text_words = str(text).lower().split()
    updated_words = []
    
    for word in text_words:
        if (word != "2fa") and is_alphanumeric(word) and (word[0].isdigit() or word[-1].isdigit()): # first or last is digit
            new_word = re.findall('\d+|\D+', word)
            updated_words.extend(new_word)
        else:
            updated_words.append(word)
    text_words = updated_words


    for coin in coin_lst:
        if coin in text_words:
            coins.append(coin)
    return coins


# the following are excluded because articles are not sorted by date
# # from newsbtc import newsbtc_scrape
# # from bitcoinmagazine import bitcoinmagazine_scrape
# # from blockonomi import blockonomi_scrape


""" Scrapes all crypto sites when an entity is queried. """

def crypto_scrape_by_entity(entity, start_date, end_date):
    # create output dataframe
    column_names = ['domain', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category','coin']

    df = pd.DataFrame(columns = column_names)


    functions_lst = [bitcoinist_scrape, cryptonews_scrape, cryptoslate_scrape]


    for f in functions_lst:
        df_website = f(entity, start_date, end_date)
        website_name = f.__name__[: -7]
        print(f'done scraping from {website_name}')
        df_website['domain'] = website_name
        df = df.append(df_website)
    
    # get text column
    df["text"] = df["title"].fillna("") + " " + df["excerpt"].fillna("")
    
    # filter out irrelevant data
    mask1 = list(df.apply(lambda x: filter_out(x["title"]) and filter_out(x["excerpt"]), axis=1))
    df = df[mask1]
    mask2 = list(df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    df = df[mask2]

    # label entity and group duplicates
    df["entity"] = entity
    df = process_duplicates(df)

    # get coins that are relevant in text 
    df['coin'] = df['text'].apply(lambda x: get_coins(x))

    # reset index
    df = df.reset_index(drop=True)

    df = df.rename({'text':'content', 'article_url':'url', 'domain':'source', \
                    'date_time':'article_date', 'image_url':'img_link'}, axis = 1)

    print(df.dtypes)
                    
    return df


""" Scrapes all crypto sites when an entity list is queried. """

def crypto_scrape(entity_list, start_date, end_date):
    column_names = ['domain', 'entity', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category', 'coin']

    df = pd.DataFrame(columns = column_names)

    # i = 0
    for entity in entity_list:
        # print(i, entity)
        print(f'======entity======')
        entity_df = crypto_scrape_by_entity(entity, start_date, end_date)
        entity_df['entity'] = entity
        df = df.append(entity_df)
        # i += 1

    # drop columns where all rows are nan
    df = df.dropna(axis=1, how='all')

    # reset index
    df = df.reset_index(drop = True)

    return df


# #### TESTING CRYPTO SCRAPE BY ENTITY FUNCTION ###
# entity = 'binance'
# start_date = datetime(2020, 9, 1)
# end_date = datetime(2020, 10, 25)
# test_df = crypto_scrape_by_entity(entity=entity, start_date=start_date, end_date=end_date)
# print(test_df)
# #################################################

#### TESTING CRYPTO SCRAPE FUNCTION ###
entity_list = list(pd.read_csv("./entity_list.csv")['entity'])
start_date = datetime(2020, 10, 30)
end_date = datetime(2020, 11, 1)
data = crypto_scrape(entity_list, start_date, end_date)
#################################################

#### TESTING CRYPTO SCRAPE FUNCTION ###
#entity_list = list(pd.read_csv("data/entity_list.csv")['entity'])
# start_date = datetime(2020, 10, 10)
# end_date = datetime(2020, 10, 25, 23, 59, 59)
# df = crypto_scrape_by_entity('huobi', start_date, end_date)
#################################################