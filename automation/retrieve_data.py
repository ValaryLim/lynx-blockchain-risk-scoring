from datetime import datetime
import pandas as pd
import numpy as np
import uuid

#Import model
from model_predict import model_predict

#Import all scrapers
import sys
sys.path.insert(1, '../scraping')
from main_conventional import conventional_scrape_by_entity
from main_crypto import crypto_scrape_by_entity
from reddit import reddit_scrape_by_entity
from twitter_twint import twitter_scrape_by_entity



def retrieve_data(entity, start_date, end_date):
    '''
    Takes in an entity name, start date and end date and returns a dataframe of scraped data from all sources

    Input:
        entity (string): 
        start_date (datetime): datetime object to specify date to start retrieving data from
        end_date (datetime): datetime object to specify date to end retrieving data
    Output: 
        df(dataframe): dataframe containing all scraped data where 
                        columns = ['uid', 'source_id', 'source', 'article_date','content', 'url','count','img_link',
                        'entity','author','ground_truth_risk','probability_risk','predicted_risk','coin']
    '''

    print('conv')
    #Conventional data processing
    conv_df = conventional_scrape_by_entity(entity, start_date, end_date)
    
    print('crypto')
    #Crypto news data processing
    crypto_df = crypto_scrape_by_entity(entity, start_date, end_date)
    
    print('twitter')
    #Twitter scraping
    twitter_df = twitter_scrape_by_entity(entity, start_date, end_date)

    print('reddit')
    #Reddit scraping
    reddit_df = reddit_scrape_by_entity(entity, start_date, end_date)

    print('scraping done...')

    #Create dataframe consisting of all required columns 
    df = pd.DataFrame(columns = ['uid', 'source_id', 'source','article_date','content', 'url','count','img_link',\
        'entity','author','ground_truth_risk','probability_risk','predicted_risk','coin'])

    #Join dataframes
    df = df.append(conv_df, ignore_index = True)
    df = df.append(crypto_df, ignore_index = True)
    df = df.append(twitter_df, ignore_index = True)
    df = df.append(reddit_df, ignore_index = True)
    
    #Fill NA with ''
    df = df.fillna('')

    #format data
    df['coin'] = df['coin'].apply(lambda x: str(x))	

    #Get risk level of articles
    if df.empty:
        df['ground_truth_risk'], df['probability_risk'], df['predicted_risk'] = '','',''		
    else:
        df['ground_truth_risk'], df['probability_risk'], df['predicted_risk'] = model_predict(df['content'])

    #Get unique id (primary key)
    df['uid'] = [str(uuid.uuid4()) for _ in range(len(df.index))]
    
    return df
    


########## Testing #############
# df = retrieve_data('okex', datetime(2020,10,20), datetime(2020,11,2))
# df.to_csv(r'~/Desktop/test_retrieval.csv', index = False)

# df = retrieve_data("okex", datetime(2020,11,1), datetime(2020,11,2))
# df.to_csv(r'~/Desktop/test.csv')
