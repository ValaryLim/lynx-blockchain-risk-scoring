import twint
import pandas as pd
import datetime as dt
from datetime import datetime
from func_timeout import func_timeout, FunctionTimedOut
from utils.get_coins import get_coins

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
    df["date_time"] = df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    df['author'] = df['username']
    df['text'] = df ['tweet']
    df['coin'] = df['text'].apply(lambda x: get_coins(x))

    df = df[['date_time', 'text', 'author', 'article_url', 'entity', 'data-item-id', 'coin']]

    df['source'] = 'twitter'

    df = df.rename({'data-item-id':'source_id','text':'content','url':'article_url',\
                    'date_time':'article_date'}, axis = 1)

    return df

def get_tweet(config):
    twint.run.Search(config) 
    tlist = config.search_tweet_list
    
    return tlist


# entity = 'okex'
# start_date = datetime(2020, 10, 15)
# end_date = datetime(2020, 10, 27)
# df = twitter_scrape_byentity(entity, start_date, end_date)
# df.to_csv(r'~/Desktop/test_twitter.csv')

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
    
    
    
    