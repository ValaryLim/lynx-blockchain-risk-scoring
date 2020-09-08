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

# excluded because articles are not sorted by date
# # from newsbtc import newsbtc_scrape
# # from bitcoinmagazine import bitcoinmagazine_scrape
# # # loops through all articles then filter by date
# # from blockonomi import blockonomi_scrape

def crypto_scrape_by_entity(entity, start_date, end_date):
    column_names = ['domain', 'date_time', 'title', 'excerpt', \
                    'article_url', 'image_url', 'author', 'author_url', \
                    'category']

    df = pd.DataFrame(columns = column_names)

    functions_lst = [bitcoin_scrape, bitcoinist_scrape, \
                     bitnewstoday_scrape, \
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


### DATA RETRIEVAL

# retrieving from each domain for all entities
entity_csv = pd.read_csv('data/entity_list.csv')
entity_list = list(entity_csv['entity'])

column_names = ['domain', 'entity', 'date_time', 'title', 'excerpt', \
                'article_url', 'image_url', 'author', 'author_url', \
                'category']

global_df = pd.DataFrame(columns = column_names)

start_date = datetime(2018, 1, 1)
end_date = datetime(2019, 12, 31, 23, 59, 59)


for i in range(32, len(entity_list)):
    en = entity_list[i]
    df_website = cointelegraph_scrape(en, start_date, end_date)
    website_name = cointelegraph_scrape.__name__[: -7]
    df_website['domain'] = website_name
    df_website['entity'] = en
    global_df = global_df.append(df_website)
    print("scraping completed: " + str(i) + " " + en)


global_df = global_df.reset_index(drop=True)
global_df.to_csv('data/crypto/sample.csv', index=False)

# DONE
# bitcoin (checked)
# cryptoslate (checked)
# cryptonews (checked)
# forbes (checked)
# insidebitcoins (checked)
# nulltx (checked)
# bitnewstoday (X)
# # check df, has 1768 rows but 1813 rows when exported
# coindesk 
# # ERROR for 53 Crypto.com (not in DOM)
# # ERROR for 125 Liqui (WebDriverException) session deleted because of page crash
# # ERROR for 126 Liquid (WebDriverException) Disconnected
# # ERROR for 137 Million.Money
# # ERROR for 176 Trade.io

# cointelegraph
# # 20 binance
# # 32 stopped here

# UNDONE
# bitcoinist



# DATA RETRIEVAL FROM HACKS LIST
column_names = ['domain', 'entity', 'date_time', 'title', 'excerpt', \
                'article_url', 'image_url', 'author', 'author_url', \
                'category']

crypto_positive = pd.DataFrame(columns = column_names)

functions_lst = [bitcoin_scrape, \
                coindesk_scrape, \
                cryptonews_scrape, cryptoslate_scrape, \
                forbes_scrape, insidebitcoins_scrape, nulltx_scrape]

hacks_list = pd.read_csv('data/hacks_list_edited.csv')



for j in range(4, len(functions_lst)):
    f = functions_lst[j]
    website_name = f.__name__[: -7]
    print("Function: " + website_name)

    if website_name == 'forbes':
        start = 8 # stopped at Taylor
    else:
        start = 0

    for i in range(start, len(hacks_list)):
        row = hacks_list.iloc[i]
        entity = row['entity']
        start_date = datetime.strptime(row['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(row['end_date'], '%Y-%m-%d')

        df_website = f(entity, start_date, end_date)

        df_website['domain'] = [website_name] * len(df_website)
        df_website['entity'] = entity
        crypto_positive = crypto_positive.append(df_website)
        print("scraping completed: " + str(i) + " " + entity)

# EXCL COINDESK

