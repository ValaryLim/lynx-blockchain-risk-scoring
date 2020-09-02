import pandas as pd
from datetime import datetime
from bitcoin import bitcoin_scrape
from bitcoinmagazine import bitcoinmagazine_scrape
from bitnewstoday import bitnewstoday_scrape
from cryptonews import cryptonews_scrape
from cryptoslate import cryptoslate_scrape
from forbes import forbes_scrape
from nulltx import nulltx_scrape

# from newsbtc import newsbtc_scrape # loops through all articles

# from bitcoinist import bitcoinist_scrape # have to deal with pop-ups
# from blockonomi import blockonomi_scrape # articles not sorted by date

def crypto_scrape_by_entity(entity, start_date, end_date):
    column_names = ['domain', 'entity', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category']

    df = pd.DataFrame(columns = column_names)

    functions_lst = [bitcoin_scrape, bitcoinmagazine_scrape, \
                     bitnewstoday_scrape, cryptonews_scrape, \
                     cryptoslate_scrape, forbes_scrape, nulltx_scrape]

    for f in functions_lst:
        df_website = f(entity, start_date, end_date)
        website_name = f.__name__[: -7]
        df_website['domain'] = [website_name] * len(df_website)
        df = df.append(df_website)

    df['entity'] = [entity] * len(df)

    df = df.reset_index(drop=True)

    return df

# testing function
test_df = crypto_scrape_by_entity('binance', datetime(2020, 7, 1), datetime(2020, 9, 1))
print(test_df)



# crypto_scrape(entity_list, start_date, end_date)