## This is a placeholder ##

import pandas as pd
import numpy as np

#By dataframe
def entity_risk_score(df):
    #create new column with just the date
    df = df.copy(deep=True)
    for fmt in ('%Y-%m-%d %H:%M:%S', '%d/%m/%y %H:%M', '%d/%m/%y'):
        try:
            df['date'] = pd.to_datetime(df.article_date, format=fmt)
        except ValueError:
            pass

    df['date'] = df['date'].dt.date
    df = df[['entity', 'date', 'probability_risk', 'count']]

    df2 =  df.groupby(['entity','date']).agg("mean")
    df2.reset_index(level=0, inplace=True)
    df2.reset_index(level=0, inplace=True)
    df2['score'] = df2['probability_risk']*100
    df2 = df2[['entity', 'date', 'score']]

    return df2
    

    

