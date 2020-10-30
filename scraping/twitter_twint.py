import twint
import pandas as pd
import datetime as dt
from datetime import datetime
from func_timeout import func_timeout, FunctionTimedOut
from utils.data_filter import filter_in, filter_out, filter_entity, process_duplicates, enTweet
from langdetect import detect

def get_tweet(config):
    twint.run.Search(config) 
    tlist = config.search_tweet_list   
    return tlist

def twitter_scrape_byentity_helper(entity, start_date, end_date):

    c = twint.Config() 
    c.Search = entity 
    c.Lang = "en"
    c.Limit = 1 #this is actually number of duplicates allowed...

    # scrape by day
    output_tweets = []
    cur_day = start_date
    while cur_day < end_date:
        print("current day: ", cur_day)
        next_day = cur_day + dt.timedelta(days=1)
        c.Since = cur_day.strftime('%Y-%m-%d')
        c.Until = next_day.strftime('%Y-%m-%d')
        cur_day = next_day
        output_tweets+=get_tweet(c)
        
    
    df = pd.DataFrame.from_dict(output_tweets)
    df['entity'] = entity
    df = df.drop_duplicates(subset='tweet')
    df['article_url'] = 'https://twitter.com/' + df['username'][1:] + '/status/' + df['data-item-id']
    df['date_time'] = df['date']
    df['author'] = df['username']
    df['text'] = df ['tweet']

    # filter out irrelevant data
    mask1 = list(df.apply(lambda x: filter_out(x["text"]), axis=1))
    df = df[mask1]
    mask2 = list(df.apply(lambda x: filter_in(x["text"]), axis=1))
    df = df[mask2]
    mask3 = list(df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    df = df[mask3]
    mask4 = list(df.apply(lambda x: enTweet((x["text"]), axis=1)))
    df = df[mask4]

    # process duplicates
    df = process_duplicates(df)

    df = df[['date_time', 'text', 'author', 'article_url', 'entity']]
    return df

def twitter_scrape_byentity(entity, start_date, end_date):
    try:
        df = func_timeout(30, twitter_scrape_byentity_helper, args=(entity, start_date, end_date))
        return df
    except:
        # return empty df
        df = pd.DataFrame(columns = ['date_time', 'text', 'author', 'article_url', 'entity'])
        return df


# entity = 'binance'
# start_date = datetime(2020, 6, 1)
# end_date = datetime(2020, 6, 30)
# df = twitter_scrape_byentity(entity, start_date, end_date)

## 2020
# entities = pd.read_csv('./entity_list.csv').entity.tolist()
# start_date = datetime(2020, 1, 1)
# end_date = datetime(2020, 6, 30)

# for entity in entities:
#     try:
#         print(f"==============currently scraping {entity}...==================")
#         df = func_timeout(30, twitter_scrape_byentity, args=(entity, start_date, end_date))
#         print(df)
#         df.to_csv(f"./2020_04/{entity}.csv")
#     except:
#         continue
    
