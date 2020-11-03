import twint
import pandas as pd
import datetime as dt
from datetime import datetime
from func_timeout import func_timeout, FunctionTimedOut
from utils.data_filter import filter_in, filter_out, filter_entity, process_duplicates, enTweet
from utils.get_coins import get_coins

# get tweet by entity by day
def get_tweet(entity, cur_day, next_day):
    c = twint.Config() 
    c.Search = entity 
    c.Lang = "en"
    c.Limit = 1 #this is actually number of duplicates allowed...
    
    c.Since = cur_day.strftime('%Y-%m-%d')
    c.Until = next_day.strftime('%Y-%m-%d')
    twint.run.Search(c) 
    tlist = c.search_tweet_list   
    return tlist

def twitter_scrape_byentity(entity, start_date, end_date):

    # scrape by day
    output_tweets = []
    cur_day = start_date
    while cur_day < end_date:
        next_day = cur_day + dt.timedelta(days=1)
        try:
            new_tweets=func_timeout(5, get_tweet, args=(entity, cur_day, next_day))
            output_tweets+=new_tweets
            #print(output_tweets)
            cur_day = next_day
        except:
            cur_day = next_day
            continue

    if(output_tweets == []):
        return pd.DataFrame()
    
    # collect information for the entity
    else: 
        df = pd.DataFrame.from_dict(output_tweets)
        df['entity'] = entity
        df['url'] = 'https://twitter.com/' + df['username'][1:] + '/status/' + df['data-item-id']
        df['date_time'] = df['date']
        df['author'] = df['username']
        df['text'] = df ['tweet']
        df['source_id'] = df['data-item-id']
        df.drop
        return df

def twitter_scrape(entity_list, start_date, end_date):
    df = pd.DataFrame()
    for entity in entity_list:
        # print(f'==={entity}===')
        try:
            curDf = twitter_scrape_byentity(entity, start_date, end_date)
            # print('----raw----')
            # print(curDf)
            df = df.append(curDf)
        except:
            continue

    df['source'] = 'twitter'
    df['coin'] = df['text'].apply(lambda x: get_coins(x))

    #print("----before processing----")
    #print(df)

    # filter out irrelevant data
    mask1 = list(df.apply(lambda x: filter_out(x["text"]), axis=1))
    df = df[mask1]
    mask2 = list(df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    df = df[mask2].reset_index(drop=True)
    mask3 = list(df['text'].apply(lambda x: enTweet((x))))
    df = df[mask3]

    df = process_duplicates(df)
    df['article_date'] = df['date_time']
    df['content'] = df['text']
    # print("----after processing----")
    # print(df)
    return df


## test (same as how the scraper would be called from automated retrieve_data)
# entity_list = pd.read_csv('./entity_list.csv').entity.tolist()[20:30]
# start_date = datetime(2020, 10, 29)
# end_date = datetime(2020, 11, 1)
# print('twitter')
# #Twitter scraping
# twitter_df = twitter_scrape(entity_list, start_date, end_date)
# if list(twitter_df.columns.values) != []:
#     twitter_df = twitter_df[['source_id', 'source','article_date','content','count','entity','author','coin']]
# print(twitter_df)
# print('scraping done...')
    
