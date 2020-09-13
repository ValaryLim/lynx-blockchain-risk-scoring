import pandas as pd
from datetime import datetime
from bitcoin import bitcoin_scrape
from bitcoinist import bitcoinist_scrape #
from bitnewstoday import bitnewstoday_scrape
from coindesk import coindesk_scrape #
from cointelegraph import cointelegraph_scrape #
from cryptonews import cryptonews_scrape #
from cryptoslate import cryptoslate_scrape #
from forbes import forbes_scrape #
from insidebitcoins import insidebitcoins_scrape
from nulltx import nulltx_scrape

# means it requires selenium

# the following are excluded because articles are not sorted by date
# # from newsbtc import newsbtc_scrape
# # from bitcoinmagazine import bitcoinmagazine_scrape
# # from blockonomi import blockonomi_scrape


""" Scrapes all crypto sites when an entity is queried. """

def crypto_scrape_by_entity(entity, start_date, end_date):
    # create output dataframe
    column_names = ['domain', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category']

    df = pd.DataFrame(columns = column_names)

    # check current date
    today = datetime.now()

    # time difference
    time_delta = (today - start_date).date

    # retrieve from sites that require selenium
    # only for recent articles
    if time_delta <= 31:
        functions_lst = [bitcoin_scrape, bitcoinist_scrape, \
                        bitnewstoday_scrape, coindesk_scrape, \
                        cointelegraph_scrape, cryptonews_scrape, \
                        cryptoslate_scrape, forbes_scrape, \
                        insidebitcoins_scrape, nulltx_scrape]

    # else, scrape only sites that use BeautifulSoup                   
    else:
        functions_lst = [bitcoin_scrape, bitnewstoday_scrape, \
                         insidebitcoins_scrape, nulltx_scrape]


    for f in functions_lst:
        df_website = f(entity, start_date, end_date)
        website_name = f.__name__[: -7]
        df_website['domain'] = [website_name] * len(df_website)
        df = df.append(df_website)
        print("scraping completed: " + website_name)

    df = df.reset_index(drop = True)

    return df


""" Scrapes all crypto sites when an entity list is queried. """

def crypto_scrape(entity_list, start_date, end_date):
    column_names = ['domain', 'entity', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category']

    df = pd.DataFrame(columns = column_names)

    for entity in entity_list:
        entity_df = crypto_scrape_by_entity(entity, start_date, end_date)
        entity_df['entity'] = entity
        df = df.append(entity_df)
    
    df = df.reset_index(drop = True)
    return df


# testing function
# test_df = crypto_scrape_by_entity('binance', datetime(2020, 7, 1), datetime(2020, 9, 1))
# print(test_df)

# entity_csv = pd.read_csv('data/entity_list.csv')
# entity_list = list(entity_csv['entity'])
# start_date = datetime(2018, 1, 1)
# end_date = datetime(2019, 12, 31, 23, 59, 59)
# test_df2 = crypto_scrape(entity_list, start_date, end_date)