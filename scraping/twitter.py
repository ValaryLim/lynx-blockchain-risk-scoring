'''
you need to make modifications mannually to your twitterscraper package to prevent 
the situation where no tweets get scraped.

refer to this link: https://github.com/taspinar/twitterscraper/pull/337/files
'''

import pandas as pd
from twitterscraper import query_tweets
from datetime import datetime

def twitter_scrap(entity, start_date, end_date, parallel_processes):
    
    '''
    parallel processes speed up the scraping process.
    advice given is to set it equal to the number of days btw start and end. 
    but the max you should set is 150.
    '''
    new_tweets = query_tweets(
            "binance",
            begindate=start_date.date(),
            enddate=end_date.date(),
            poolsize=parallel_processes)
    
    # get the relevant attributes of tweets
    tweet_list = []
    for tweet in new_tweets:
        new_tweet = [
            tweet.timestamp,
            tweet.tweet_id,
            tweet.text,
            tweet.tweet_url,
            tweet.username,
            tweet.user_id,
            tweet.links,
            tweet.hashtags
        ]
        tweet_list.append(new_tweet)
    
    df = pd.DataFrame(tweet_list)
    df.columns = ['date_time','tweet_id','text','tweet_url',
                          'username','user_id','links','hashtags']
    
    return df


# test
# entity = 'binance'
# start_date = datetime(2020, 5, 2)
# end_date = datetime(2020, 5, 3)
# df = twitter_scrap(entity, start_date, end_date, 1)


