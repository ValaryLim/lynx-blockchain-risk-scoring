import pandas as pd
from datetime import datetime
from bitcoin import bitcoin_scrape
from bitcoinist import bitcoinist_scrape #
from bitnewstoday import bitnewstoday_scrape
from coindesk import coindesk_scrape
from cointelegraph import cointelegraph_scrape
from cryptonews import cryptonews_scrape #
from cryptoslate import cryptoslate_scrape #
from forbes import forbes_scrape
from insidebitcoins import insidebitcoins_scrape
from nulltx import nulltx_scrape

# import sys
# sys.path.insert(1, './utils')
from utils.data_filter import filter_out, filter_entity, process_duplicates
from utils.get_coins import get_coins


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


    functions_lst = [bitcoin_scrape, bitnewstoday_scrape, \
                     insidebitcoins_scrape, nulltx_scrape, \
                     cointelegraph_scrape, coindesk_scrape, \
                     forbes_scrape]


    for f in functions_lst:
        df_website = f(entity, start_date, end_date)
        website_name = f.__name__[: -7]
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
# entity_list = list(pd.read_csv("data/entity_list.csv")['entity'])
# start_date = datetime(2020, 1, 1)
# end_date = datetime(2020, 6, 30, 23, 59, 59)
# data = crypto_scrape(entity_list, start_date, end_date)
#################################################

#### TESTING CRYPTO SCRAPE FUNCTION ###
#entity_list = list(pd.read_csv("data/entity_list.csv")['entity'])
# start_date = datetime(2020, 10, 10)
# end_date = datetime(2020, 10, 25, 23, 59, 59)
# df = crypto_scrape_by_entity('huobi', start_date, end_date)
#################################################
