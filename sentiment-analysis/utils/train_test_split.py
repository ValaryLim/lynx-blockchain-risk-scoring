import pandas as pd
from datetime import datetime

def try_parsing_date(text):
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%y %H:%M', '%d/%m/%y'):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            pass

        except TypeError:
            return text
        
    raise ValueError('no valid date format found')


#Return train set (60%), validation set(20%), test set(20%)
def train_val_test_split(filepath):
    df = pd.read_csv(filepath, low_memory = False, encoding= 'latin-1')

    #Convert all date_time to datetime format
    df['date_time'] = df['date_time'].apply(lambda x: try_parsing_date(x))
    df = df[df['date_time'].notna()]

    
    #Sort df by date_time
    df = df.sort_values('date_time', ascending = True)
    df = df.reset_index(drop=True)

    #Num of rows in the dataframe
    numrows = df.shape[0]

    #Retrieve just the date 
    df['date'] =  df['date_time'].apply(lambda x: x.date())

    #Get training dataset
    #Get last date for the train set and get the data rows that fall within the date range
    train_index = int(0.6*numrows) - 1
    last_date1 = df.iloc[train_index]['date']
    train = df[df['date'] <= last_date1]
    train = train.drop(['date','Unnamed: 0'], axis = 1)
    
    #Get validation dataset
    num_rows_required = int(0.2*numrows) 
    val_index = train.shape[0]
    last_date2 = df.iloc[val_index + num_rows_required - 1]['date']
    mask = (df['date'] > last_date1) & (df['date'] <= last_date2)
    val = df.loc[mask]
    val = val.drop(['date','Unnamed: 0'], axis = 1)

    #Get testing dataset
    test = df[df['date'] > last_date2]
    test = test.drop(['date','Unnamed: 0'], axis = 1)

    return train, val, test




#Return train set (80%), test set(20%)
def train_test_split(filepath):
    df = pd.read_csv(filepath, low_memory = False, encoding= 'latin-1')

    #Convert all date_time to datetime format
    df['date_time'] = df['date_time'].apply(lambda x: try_parsing_date(x))
    df = df[df['date_time'].notna()]

    #Sort df by date_time
    df = df.sort_values('date_time', ascending = True)
    df = df.reset_index(drop=True)

    #Num of rows in the dataframe
    numrows = df.shape[0]

    #Retrieve just the date 
    df['date'] =  df['date_time'].apply(lambda x: x.date())

    #Get training dataset
    #Get last date for the train set and get the rows that fall within the date range
    train_index = int(0.8*numrows) - 1
    last_date = df.iloc[train_index]['date']
    train = df[df['date'] <= last_date]
    train = train.drop(['date','Unnamed: 0'], axis = 1)

    #Get testing dataset
    test = df[df['date'] > last_date]
    test = test.drop(['date','Unnamed: 0'], axis = 1)

    return train, test


