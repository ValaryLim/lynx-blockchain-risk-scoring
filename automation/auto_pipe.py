from datetime import datetime
import pandas as pd
import numpy as np
import sqlite3

#Import data retrieval function
from retrieve_data import retrieve_data
from model_train import model_train
from entity_risk_score import entity_risk_score


def get_data(entity_list, start_date, end_date):
    '''
    Input:
        entity_list (list):
        start_date (datetime):
        end_date (datetime):
    '''

    #Connect to database
    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    # Retrieve data from web scraping and store in database
    # for entity:
    #     df = retrieve_data(entity_list, start_date, end_date)
    #     score = 
    #     score["entity"] = entity
    
    df = retrieve_data(entity, start, end)
    
    
    #df.to_csv(r'~/Desktop/test.csv', index = False)

    #Append data into table
    df.to_sql('POST_DATA', conn, if_exists='append', index = False)

    entity_df = entity_risk_score(df)
    entity_df.to_sql('ENTITY_DATA', conn, if_exists='append', index = False)

    conn.close()

    return 


############# Testing #############
#get_data(['binance','bitfinex', 'huobi', 'okex', 'upbit'], datetime(2020,9,1), datetime(2020,10,26))
###################################


def train(filepath):
    '''
    Retrain model and update the model used in model_predict

    Input:
        filepath (str): path to store new model
    '''
    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    # Get all data from database as dataframe
    c.execute('''
        SELECT * FROM POST_DATA
        ''')

    df = pd.DataFrame(c.fetchall(), columns = ['uid', 'source_id', 'source','article_date','content', 'url', 'count',\
                    'img_link','entity','author','ground_truth_risk','probability_risk','predicted_risk','coin'])  
    
    #Retrain model
    model_train(df, output_dir= filepath)
    
    #Modify the model being used in model_predict through curr_model.txt
    path = open("../automation/curr_model.txt", "w")
    path.write(filepath)
    path.close()


    return 


