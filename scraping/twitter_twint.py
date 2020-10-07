import twint
import pandas as pd
import datetime as dt
from datetime import datetime


def twitter_scrape_byentity(entity, start_date, end_date):

    c = twint.Config() 
    c.Search = entity 
    c.Limit = 100 #max 100 per entity per month

    months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    if months <= 1:
        c.Since = start_date.strftime('%Y-%m-%d')
        c.Until = end_date.strftime('%Y-%m-%d')

        # tweets selection condition to be customised
        # c.Min_likes = 500
        # c.Min_retweets = 50
        # c.Min_replies = 50

        twint.run.Search(c) 
        tlist = c.search_tweet_list

        # convert from json to pandas df and return
        df = pd.DataFrame.from_dict(tlist) 
        df['entity'] = entity
        return df

    else:

        #scrap by month to ensure a good disrtibution of tweets
        for i in range(months):

            # create empty df to be updated
            df = pd.DataFrame()
            
            curStart = start_date + dt.timedelta(days=i*30)
            curEnd = end_date + dt.timedelta(days=i*30)
            c.Since = start_date.strftime('%Y-%m-%d')
            c.Until = end_date.strftime('%Y-%m-%d')

            # tweets selection condition to be customised
            c.Min_likes = 500
            c.Min_retweets = 50
            c.Min_replies = 50

            twint.run.Search(c) 
            curTlist = c.search_tweet_list

            # append to df
            cDf = pd.DataFrame.from_dict(curTlist)
            df = df.append(cDf)
            df['entity'] = entity

        return df


# entity = 'binance'
# start_date = datetime(2020, 5, 2)
# end_date = datetime(2020, 5, 4)
# df = twitter_scrape_byentity(entity, start_date, end_date)
# print(df)