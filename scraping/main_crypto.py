import pandas as pd
from datetime import datetime
from bitcoin import bitcoin_scrape
from bitcoinist import bitcoinist_scrape #
from bitcoinmagazine import bitcoinmagazine_scrape
from bitnewstoday import bitnewstoday_scrape
from coindesk import coindesk_scrape #
from cointelegraph import cointelegraph_scrape #
from cryptonews import cryptonews_scrape #
from cryptoslate import cryptoslate_scrape #
from forbes import forbes_scrape #
from insidebitcoins import insidebitcoins_scrape
from nulltx import nulltx_scrape

# means it requires selenium

# excluded because articles are not sorted by date
# # from newsbtc import newsbtc_scrape
# # # loops through all articles then filter by date
# # from blockonomi import blockonomi_scrape

def crypto_scrape_by_entity(entity, start_date, end_date):
    column_names = ['domain', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category']

    df = pd.DataFrame(columns = column_names)

    functions_lst = [bitcoin_scrape, bitcoinist_scrape, \
                     bitcoinmagazine_scrape, bitnewstoday_scrape, \
                     coindesk_scrape, cointelegraph_scrape, \
                     cryptonews_scrape, cryptoslate_scrape, \
                     forbes_scrape, insidebitcoins_scrape, nulltx_scrape]

    for f in functions_lst:
        df_website = f(entity, start_date, end_date)
        website_name = f.__name__[: -7]
        df_website['domain'] = [website_name] * len(df_website)
        df = df.append(df_website)
        print("scraping completed: " + website_name)

    df = df.reset_index(drop = True)

    return df

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