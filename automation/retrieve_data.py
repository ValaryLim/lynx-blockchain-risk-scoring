from datetime import datetime
import pandas as pd
import numpy as np
import uuid

#Import model
from model_predict import model_predict

#Import all scrapers
import sys
sys.path.insert(1, '../scraping')
from main_conventional import conventional_scrape
from main_crypto import crypto_scrape
from reddit import reddit_scrape
from twitter_twint import twitter_scrape



def retrieve_data(entity_list, start_date, end_date):
    '''
    Takes in a list of entities, start date and end date and returns a dataframe of scraped data from all sources

    Input:
        lst (entity_list)
        start_date (datetime): datetime object to specify date to start retrieving data from
        end_date (datetime): datetime object to specify date to end retrieving data
    Output: 
        df (dataframe): dataframe containing all scraped data 
    '''

    print('conv')
    #Conventional data processing
    conv_df = conventional_scrape(entity_list, start_date, end_date)
    if list(conv_df.columns.values) != []:
        conv_df = conv_df[['source','article_date','content', 'url','count','entity','coin']]
    

    print('crypto')
    #Crypto news data processing
    crypto_df = crypto_scrape(entity_list, start_date, end_date)
    if list(crypto_df.columns.values) != []:
        crypto_df = crypto_df[['source','article_date','content', 'url','count','img_link','entity','author','coin']]
    

    print('reddit')
    #Reddit scraping
    reddit_df = reddit_scrape(entity_list, start_date, end_date)
    if list(reddit_df.columns.values) != []:
        reddit_df = reddit_df[['source','article_date','content', 'url','count','entity','author','coin']]


    print('twitter')
    #Twitter scraping
    twitter_df = twitter_scrape(entity_list, start_date, end_date)
    if list(twitter_df.columns.values) != []:
        twitter_df = twitter_df[['source_id', 'source','article_date','content','count','entity','author','coin']]

    print('scraping done...')


    #Create dataframe consisting of all required columns 
    df = pd.DataFrame(columns = ['uid', 'source_id', 'source','article_date','content', 'url','count','img_link',\
        'entity','author','ground_truth_risk','probability_risk','predicted_risk','coin'])

    df = df.append(conv_df)
    df = df.append(crypto_df)
    df = df.append(reddit_df)
    df = df.append(twitter_df)

    #format data
    df['coin'] = df['coin'].apply(lambda x: str(x))	

    #Get risk level of articles
    if df.empty:
        df['ground_truth_risk'], df['probability_risk'], df['predicted_risk'] = '','',''		
    else:
        df['ground_truth_risk'], df['probability_risk'], df['predicted_risk'] = model_predict(df['content'])

    #Get unique id (primary key)
    df['uid'] = [str(uuid.uuid4()) for _ in range(len(df.index))]
    
    #Fill NA with ''
    df = df.fillna('')

    return df
    


########## Testing #############
# df = retrieve_data(['huobi'], datetime(2020,6,25), datetime(2020,10,26))
# df.to_csv(r'~/Desktop/test_retrieval.csv', index = False)