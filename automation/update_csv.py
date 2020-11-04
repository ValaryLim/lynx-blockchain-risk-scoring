import pandas as pd

def update_csv(df_new, original_filepath):
    '''
    For dashboard usage: Update csv based on new data retrieved each time

    Input:
        df_new (dataframe): dataframe consisting of newly retrieved data
        original_filepath(string): Update csv file with newly retrieved data

    '''
    
    df_new = df_new.fillna("")
    df_new.to_csv(original_filepath, mode='a', header=False, index = False)

    return 

