import twint
import pandas as pd
import datetime as dt
from datetime import datetime

import sys
sys.path.insert(1, './utils')
from data_filter import filter_in, filter_out, enTweet, filter_entity, process_duplicates

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

    # process all tweets
    # standardise columns
    print(df.head())
    df["date_time"] = df["date"].apply(lambda x: datetime.strptime(x, "%Y-%m-%d"))
    df["text"] = df["tweet"]
    df['entity'] = entity
    df = df[["date_time", "text", "entity", "username", "avatar", "data-item-id", "data-conversation-id"]]

    # filter only english tweets
    print(df.head())
    mask1 = list(df.apply(lambda x: enTweet(x["text"]), axis=1))
    df = df[mask1]

    # filter in and out terms
    print(df.head())
    mask2 = list(df.apply(lambda x: filter_out(x["text"]), axis=1))
    df = df[mask2]
    mask3 = list(df.apply(lambda x: filter_in(x["text"]), axis=1))
    df = df[mask3]
    mask4 = list(df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    df = df[mask4]
    
    # process duplicates
    df = process_duplicates(df)
    print(df.head())

    # reset index
    df = df.reset_index(drop=True)

    return df

def twitter_scrape(entity_list, start, end):
    #Create empty dataframe
    output_df = pd.DataFrame()

    #Iterate through list of entities
    for entity in entity_list:
        #retrieve dataframe consisting of all data for each entity
        df = twitter_scrape_byentity(entity, start, end)

        #Join the dataframes by column
        output_df = output_df.append(df)

    # reset index
    output_df = output_df.reset_index(drop=True)

    return output_df


# entity = 'binance'
# start_date = datetime(2020, 1, 2)
# end_date = datetime(2020, 10, 15)
# df = twitter_scrape_byentity(entity, start_date, end_date)
# print(df)