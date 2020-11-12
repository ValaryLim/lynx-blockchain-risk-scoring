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

from utils.data_filter import filter_out, filter_entity, process_duplicates
from utils.get_coins import get_coins

# the following are excluded because articles are not sorted by date
# # from newsbtc import newsbtc_scrape
# # from bitcoinmagazine import bitcoinmagazine_scrape
# # from blockonomi import blockonomi_scrape


def crypto_scrape_by_entity(entity, start_date, end_date):
    '''
    Retrieves articles relating to entity from crypto news sites within the stipulated time frame 

    Input:
        entity(string): entity name to retrieve data on
        start_date(datetime): date to begin scraping from
        end_date(datetime): date to stop scraping
    Output:
        df(dataframe): dataframe with columns = [entity	title, excerpt, category, coin, source, article_date,	
                                url, img_link, content, count, date_time_all, author, author_url, source_id]
    '''

    entity = entity.lower()

    # create output dataframe
    column_names = ['domain', 'date_time', 'title', 'excerpt', 'entity' \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category','coin', 'source_id']

    df = pd.DataFrame(columns = column_names)

    functions_lst = [bitcoin_scrape, bitcoinist_scrape, bitnewstoday_scrape, \
                     coindesk_scrape, cointelegraph_scrape, cryptonews_scrape,\
                     cryptoslate_scrape, coindesk_scrape, forbes_scrape,\
                     insidebitcoins_scrape, nulltx_scrape]

    for f in functions_lst:
        # call functions to scrape data from individual websites
        df_website = f(entity, start_date, end_date)
        website_name = f.__name__[: -7]
        df_website['domain'] = website_name
        # append data to output dataframe
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

    # rename dataframe using naming convention in final database
    df = df.rename({'text':'content', 'article_url':'url', 'domain':'source', \
                    'date_time':'article_date', 'image_url':'img_link'}, axis = 1)
    
    # keep only relevant columns
    df = df[['source','source_id','article_date','content', 'url','count','img_link', 'entity','author','coin']]

    return df



def crypto_scrape(entity_list, start_date, end_date):
    # create output dataframe
    column_names = ['domain', 'entity', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category', 'coin', 'source_id']

    df = pd.DataFrame(columns = column_names)

    # loop through list of entities and scrape all sites for each entity
    for entity in entity_list:
        entity_df = crypto_scrape_by_entity(entity, start_date, end_date)
        df = df.append(entity_df)

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
# entity_list = list(pd.read_csv("data/entity_list.csv")['entity'])
# start_date = datetime(2020, 10, 10)
# end_date = datetime(2020, 10, 25, 23, 59, 59)
# df = crypto_scrape_by_entity('huobi', start_date, end_date)
#################################################
