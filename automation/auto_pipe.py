from datetime import datetime
import pandas as pd
import numpy as np
import sqlite3
import logging

from retrieve_data import retrieve_data
from model_train import model_train
from model_eval import model_eval

# import risk scoring function
import sys
sys.path.insert(1, '../scoring/utils')
from scoring_automated import entity_risk_score
sys.path.remove('../scoring/utils')

# for dashboard
# from update_csv import update_csv


def get_data_all(entity_list, start_date, end_date):
    '''
    Retrieve and store retrieved data on all entities in database

    Input:
        entity (string): name of entity to query
        start_date(datetime): date to start data retrieval
        end_date(datetime): date to end data retrieval
    '''
    # Get all data into database
    for entity in entity_list:
        print(entity)
        get_data(entity, start_date, end_date)
    
    # Get overall risk score after running the query
    get_overall_risk(start_date, end_date)

    return 



def get_data(entity, start_date, end_date):
    '''
    Retrieve and store data on entity in database

    Input:
        entity (string): name of entity to query
        start_date(datetime): date to start data retrieval
        end_date(datetime): date to end data retrieval
    '''

    #Connect to database
    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    # Scrape data and predict
    try:
        df = retrieve_data(entity, start_date, end_date)
        
        #Append data into table
        df.to_sql('POST_DATA', conn, if_exists='append', index = False)
        # update_csv(df, '../automation/data/all_predicted_2020.csv')

        #Get dataframe of risk scores by date and entity
        entity_df_tem = entity_risk_score(df, entity, start_date, end_date)
        entity_df = entity_df_tem[["date", "entity", "score"]]

        #Store data into table in database
        entity_df.to_sql('ENTITY_DATA', conn, if_exists='append', index = False)
        # update_csv(entity_df_tem, '../automation/data/entity_risk_score_2020.csv')
    
    # catch exceptions and log to error_log.log file
    except Exception as e:

        logging.basicConfig(filename='../automation/error_log.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

        logger = logging.getLogger(__name__)

        logger.exception(e)

    #Close connection
    conn.close()

    return 


############# Testing #############
# get_data('okex', datetime(2020,1,1), datetime(2020,11,11))

# entity_list = pd.read_csv('../automation/utils/data/entity_list')['entity'].tolist()
# for entity in entity_list:
#     retrieve_data(entity, start_date, end_date)
###################################


def get_overall_risk(start_date, end_date):
    '''
    Query DB1, calculate and store overall entity risk score in DB2

    Input:
        start_date(datetime): date to start data retrieval
        end_date(datetime): date to end data retrieval
    '''

    #Connect to database
    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    # Get all data within date range from database (POST_DATA table) as dataframe 
    c.execute('''
            SELECT * FROM POST_DATA
            WHERE (article_date BETWEEN ? AND ?)
            ''', (start_date, end_date))

    df = pd.DataFrame(c.fetchall(), columns = list(map(lambda x: x[0], c.description)))  

    df = df.fillna("")

    #Get dataframe of risk scores by date and entity
    entity_df_tem = entity_risk_score(df, entity="overall", start_date=start_date, end_date=end_date)
    entity_df = entity_df_tem[["date", "entity", "score"]]

    #Store data into table in database
    entity_df.to_sql('ENTITY_DATA', conn, if_exists='append', index = False)
    #update_csv(entity_df_tem, '../automation/data/entity_risk_score_2020.csv')

    #Close connection
    conn.close()

    return 


def train(filepath, train_start_date, train_end_date, eval_start_date = None, eval_end_date = None):
    '''
    Retrain model and update the model used in model_predict

    Input:
        filepath (str): path to store new model
        train_start_date (datetime): date to start retrieivng data from database for training
        train_end_date (datetime): date to end retrieivng data from database for training
        eval_start_date (datetime): date to start retrieivng data from database for evaluation
        eval_end_date (datetime): date to end retrieivng data from database for evaluation
    '''

    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    # Convert datetime object to string for parsing into database query
    train_start = train_start_date.strftime('%Y-%m-%d %H:%M:%S')
    train_end = train_end_date.strftime('%Y-%m-%d %H:%M:%S')

    # Get all data within date range from database (POST_DATA table) as dataframe 
    c.execute('''
            SELECT * FROM POST_DATA
            WHERE (article_date BETWEEN ? AND ?)
            ''', (train_start, train_end))

    df = pd.DataFrame(c.fetchall(), columns = list(map(lambda x: x[0], c.description))) 

    conn.close()

    
    # Retrain model
    model_train(df, output_dir= filepath)

    # Evaluate metrics 
    if eval_start_date != None or eval_end_date != None:
        model_eval(eval_start_date, eval_end_date, filepath)

    return 


def deploy(filepath):
    '''
    Deploy model 

    Input:
        filepath (str): path to new model to be deployed
    '''
    path = open("../automation/curr_model.txt", "w")
    path.write(filepath)
    path.close()

    return 


def clear_log():
    '''
    Clears log file that may have come from previous runs
    '''
    with open('../automation/error_log.log', 'w'):
        pass


####################### How to run ########################

################ retrieving data ################
# entity_list = pd.read_csv(r'./utils/data/entity_list.csv')['entity'].tolist()
# clear_log()
# for entity in entity_list:
#   print(entity)
#   get_data(entity, datetime(2020,11,12), datetime(2020,11,13))

################ training & deployment ################
# filepath = '../automation/models/new_test_model'
# train_start_date = datetime(2020,10,1)
# train_end_date = datetime(2020,10,25,23,59,59)
# eval_start_date = datetime(2020,10,26)
# eval_end_date = datetime(2020,10,30,23,59,59)

# train(filepath, train_start_date, train_end_date, eval_start_date = eval_start_date, eval_end_date = eval_end_date)
# # if results satisfactory for deployment
# deploy(filepath)

