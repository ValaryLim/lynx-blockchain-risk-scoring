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



def train_test_split(filepath):
    df = pd.read_csv(filepath, low_memory = False, encoding= 'latin-1')

    cols = list(df.columns) 
    print(cols)

    if 'text' not in cols:
        df['excerpt'] = df['excerpt'].fillna('')
        df['text'] = df.title + '. ' + df.excerpt


    #Convert all date_time to datetime format
    df['date_time'] = df['date_time'].apply(lambda x: try_parsing_date(x))
    df = df[df['date_time'].notna()]

    #Sort df by date_time
    df = df.sort_values('date_time', ascending = True)

    last_date = datetime(2019,5,14,23,59,59)

    #Get training dataset
    #Get last date for the train set and get the rows that fall within the date range
    train = df[df['date_time'] <= last_date]
    train = train[['date_time','label','text']]

    #Get testing dataset
    test = df[df['date_time'] > last_date]
    test = test[['date_time','label','text']]

    return train, test

