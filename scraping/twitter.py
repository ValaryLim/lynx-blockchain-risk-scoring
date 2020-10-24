'''
you need to make modifications mannually to your twitterscraper package to prevent 
the situation where no tweets get scraped.

refer to this link: https://github.com/taspinar/twitterscraper/pull/337/files
'''

import pandas as pd
from twitterscraper import query_tweets
from datetime import datetime, timedelta
from langdetect import detect # remove non-english tweets
from nltk.sentiment.vader import SentimentIntensityAnalyzer # vader

'''
to import from the utils, need to add the directory to path.
see: https://stackoverflow.com/questions/4383571/importing-files-from-different-folder 
'''

from data_filter import filter_in, filter_out, enTweet, filter_entity, process_duplicates
from vader_filter import filter_vader

# function to scrap a single entity
def twitter_scrape_byentity(entity, start_date, end_date):
    '''
    parallel processes speed up the scraping process.
    advice given is to set it equal to the number of days btw start and end. 
    but the max you should set is 150.

    *set to 7 for hack list 
    '''
    new_tweets = query_tweets(
            entity,
            begindate=start_date.date(),
            enddate=end_date.date(),
            poolsize=7,
            lang='english', #other languages may still get returned sometimes
            limit=20)       #change the limit accordingly
    
    # get the relevant attributes of tweets
    tweet_list = []
    for tweet in new_tweets:
        new_tweet = [
            tweet.timestamp,
            tweet.text,
            tweet.tweet_url,
            tweet.tweet_id,
            tweet.username,
            tweet.user_id,
            tweet.hashtags,
            tweet.links
        ]
        tweet_list.append(new_tweet)
    
    df = pd.DataFrame(tweet_list)
    df.columns = ['date_time','text', 'tweet_url', 'tweet_id',
                    'username','user_id','hashtags', 'links']

    # filter only english tweets
    mask1 = list(df.apply(lambda x: enTweet(x["text"]), axis=1))
    df = df[mask1]

    # filter in and out terms
    mask2 = list(df.apply(lambda x: filter_out(x["text"]), axis=1))
    df = df[mask2]
    mask3 = list(df.apply(lambda x: filter_in(x["text"]), axis=1))
    df = df[mask3]
    mask4 = list(df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    df = df[mask4]
    
    # reset index
    df = df.reset_index(drop=True)
    return df


# test
# entity = 'binance'
# start_date = datetime(2020, 5, 2)
# end_date = datetime(2020, 5, 9)
# df = twitter_scrap(entity, start_date, end_date)


# combine the tweets of all entities in the hack list
# positives = pd.DataFrame(columns=['date_time','text', 'tweet_url', 'tweet_id',
#                     'username','user_id','hashtags', 'links'])

# hacks = pd.read_csv('hacks_list.csv')
# hacks['start_date'] = pd.to_datetime(hacks['start_date'])
# hacks['end_date'] = pd.to_datetime(hacks['end_date'])

# for index, row in hacks.iterrows():
#     exchange = row['exchange']
#     temp = twitter_scrap(exchange, row['start_date']- timedelta(days=1), row['end_date'])
#     print(f'adding {exchange} data to positives df...')
#     positives = positives.append(temp)
#     print(f'number of rows after appending {exchange}: {positives.shape[0]}')

# print("==============data retrieval finised=================")
# print(f'total number of tweets retrieved: {positives.shape[0]}')



# positives = positives[positives.apply(lambda x: enTweet(x["text"]), axis=1)].reset_index(drop=True)
# print(f'number of tweets after removing non-english texts: {positives.shape[0]}')

# positives = positives[positives.apply(lambda x: filter_in(x["text"]), axis=1)].reset_index(drop=True)
# print(f'number of tweets after filter_in: {positives.shape[0]}')

# positives = positives[positives.apply(lambda x: filter_out(x["text"]), axis=1)].reset_index(drop=True)
# print(f'number of tweets after filter_out: {positives.shape[0]}')

# positives = positives[positives.apply(lambda x: pd.isna(filter_vader(x["text"])), axis=1)].reset_index(drop=True)
# print(f'number of tweets after filter_vader: {positives.shape[0]}')

# positives.to_csv("tweeter_positive_tolabel.csv")
# print("==============data saved after filter=================")