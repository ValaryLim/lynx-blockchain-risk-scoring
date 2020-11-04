import pandas as pd
import datetime as datetime

def process_dataframe(df):
    if "date" in df.columns:
        df["date_time"] = df["date"]
    
    # change entity to lowercase
    df["entity"] = df["entity"].apply(lambda x: x.lower())

    # format date_time
    df = format_date_time(df)

    # retrieve date
    df["date"] = df.date_time.apply(lambda x: x.date())
    
    # select specific columns
    df = df[["date_time", "date", "text", "entity", "prob", "pred"]]

    # process duplicates
    df = process_duplicates(df, subset=["text", "entity"])
    
    return df

def process_dataframe_final(df):
    # drop those with missing entities, date, risk predictions or counts
    df = df.dropna(subset=["entity", "article_date", "predicted_risk", "count"])
    
    # change entity to lowercase
    df["entity"] = df["entity"].apply(lambda x: x.lower())
    
    # change source to lowercase
    df = df.fillna("")
    df["source"] = df["source"].apply(lambda x: x.lower())

    # add counter variable
    df["counter"] = df["count"]
    
    # format date_time
    df = format_date_time_final(df)

    # retrieve date
    df["date"] = df.article_date.apply(lambda x: x.date())
    
    return df

def format_date_time(df):
    '''
    Formats date_time column into datetime object
    '''
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%y %H:%M', '%d/%m/%y'):
        try:
            df['date_time'] = pd.to_datetime(df.date_time, format=fmt)
        except ValueError:
            pass
    
    return df

def format_date_time_final(df):
    '''
    Formats date_time column into datetime object
    '''
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%y %H:%M', '%d/%m/%y'):
        try:
            df['article_date'] = pd.to_datetime(df.article_date, format=fmt)
        except ValueError:
            pass
    
    return df

def process_duplicates(df, subset=["text", "entity"]):
    '''
    Accepts a pandas dataframe and outputs 
    '''
    if df.empty:
        df["count"] = 0
        df["date_time_all"] = []
        return df
    
    # assign count based on text and entity
    df["counter"] = df.groupby(by=subset).text.transform('size')

    # get array of all date times
    df = df.merge(df.groupby(subset).date_time.agg(list).reset_index(), 
              on=subset, 
              how='left',
                  suffixes=['', '_all'])
    
    # drop duplicates, keeping the first
    df = df.drop_duplicates(subset=subset, keep='first')

    return df

def process_duplicates_entity_independent(df):
    '''
    Accepts a pandas dataframe and outputs 
    '''
    if df.empty:
        df["counter"] = 0
        df["date_first"] = ""
        return df
    
    # assign count based on text and entity
    df["counter"] = df.groupby(by=["text"]).text.transform('size')

    # get array of all date times
    df = df.merge(df.groupby(["text"]).date_time.agg(list).reset_index(), 
              on=["text"], 
              how="left",
                  suffixes=['', '_all'])
    
    # drop duplicates, keeping the first
    df = df.drop_duplicates(subset=["text"], keep='first')

    return df
