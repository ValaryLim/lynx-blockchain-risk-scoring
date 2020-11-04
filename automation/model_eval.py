import pandas as pd
from datetime import datetime
import sqlite3
from sklearn.metrics import recall_score, precision_score, f1_score
from model_predict import model_predict 


def to_binary(prob):
    if prob > 0.5:
        return 1
    return 0

def model_eval(start_date, end_date, new_model):
    '''
    Gives metrics (recall, precision, f1) to evaluate new model against existing model

    Input:
        start_date(datetime): date to start using data for evaluation of model 
        end_date(datetime): date to end using data for evaluation of model 
        new_model(string): filepath to new model

    '''

    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    # Convert datetime object to string for parsing into database query
    start = start_date.strftime('%Y-%m-%d %H:%M:%S')
    end = end_date.strftime('%Y-%m-%d %H:%M:%S')
    
    # Get all data within date range from database (POST_DATA table) as dataframe 
    c.execute('''
            SELECT * FROM POST_DATA
            WHERE (article_date BETWEEN ? AND ?)
            ''', (start, end))
    
    df = pd.DataFrame(c.fetchall(), columns = list(map(lambda x: x[0], c.description)))  

    conn.close()

    # retrieve required data for model evaluation
    y_actual = df['ground_truth_risk']
    y_pred_old = df.apply(lambda x: to_binary(x['probability_risk']), axis=1)
    y_pred_new, _, _ = model_predict(df['content'])

    # get metrics for evaluation (original model)
    precision_original = precision_score(y_actual, y_pred_old, average="binary", pos_label=1)
    recall_original = recall_score(y_actual, y_pred_old, average="binary", pos_label=1)
    f1_original = f1_score(y_actual, y_pred_old, average="binary", pos_label=1)

    # get metrics for evaluation (new model)
    precision_new = precision_score(y_actual, y_pred_new, average="binary", pos_label=1)
    recall_new = recall_score(y_actual, y_pred_new, average="binary", pos_label=1)
    f1_new = f1_score(y_actual, y_pred_new, average="binary", pos_label=1)


    print('Evaluatoin Metrics')
    print("-------------------------------------------------")
    print('Original Model')
    print("precision:", round(precision_original, 5))
    print("recall:", round(recall_original, 5))
    print("f1:", round(f1_original, 5))
    print("-------------------------------------------------")
    print('New Model')
    print("precision:", round(precision_new, 5))
    print("recall:", round(recall_new, 5))
    print("f1:", round(f1_new, 5))
    

    return 

