import twint
import pandas as pd
import datetime as dt
from datetime import datetime
from func_timeout import func_timeout, FunctionTimedOut

def get_tweet(config):
    twint.run.Search(config) 
    tlist = config.search_tweet_list

    # tweets selection condition to be customised
    # c.Min_likes = 500
    # c.Min_retweets = 50
    # c.Min_replies = 50
    # other paramters: https://github.com/twintproject/twint/blob/master/twint/config.py

    
    return tlist

def twitter_scrape_byentity(entity, start_date, end_date):

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
    df = df[['date_time', 'text', 'author', 'article_url', 'entity']]
    return df

def get_tweet(config):
    twint.run.Search(config) 
    tlist = config.search_tweet_list
    
    return tlist


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
    
    
    
    