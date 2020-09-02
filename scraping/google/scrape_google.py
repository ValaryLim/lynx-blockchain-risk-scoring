import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime
from datetime import date
import regex as re
pd.set_option('max_colwidth', 10000)
from scrape_google_utils import *
from typing import List
from dateutil.relativedelta import *



def scrap_headlines(entity:str, start_date: str, end_date: str):
    
    '''
    Scrap (using GoogleNews API) the top 10 headlines of google news on a particular entity, for a given time range
    Output : Pandas Dataframe with title, short summary, date & url column
    '''
    
    start_date_input=datetime.strptime(start_date, "%Y-%m-%d").strftime("%m-%d-%Y")
    end_date_input=datetime.strptime(end_date, "%Y-%m-%d").strftime("%m-%d-%Y")
    news = GoogleNews(start=start_date_input,end=end_date_input, lang='en', encode='utf-8')
    news.search(f"{entity} crypto")   # Main bulk of time, taking ~2 seconds to search
    
    if pd.DataFrame(news.result()).empty:
        # No relevant articles 
        return pd.DataFrame()
    
    df = pd.DataFrame(news.result())[['title', 'desc', 'date', 'link']]
    
    # Exist date input as '1 month ago' for recent articles
    # df['date'] = pd.to_datetime(df['date'])
    
    # Only get headlines which mention the entity of interest
    df=df[df['title'].str.contains(entity,flags=re.IGNORECASE)].reset_index(drop=True)
    df['entity'] = entity
    
    return df

df=scrap_headlines('Binance', '2020-06-27','2020-08-10')


def scrap_googleNews(start_date: datetime, end_date: datetime, exchanges: List[str]):
    df=pd.DataFrame()
    for ex in exchanges:
        curDf = scrap_headlines(ex, start_date,end_date)
        df=df.append(curDf)
    
    return df

all = scrap_googleNews('2020-06-27','2020-08-10', top_exchange())


def date_convert(day): 
    if day == '1 month ago':
        return datetime.strptime((date.today() - relativedelta(months=+1)).strftime('%Y%m%d'), '%Y%m%d')
    elif day == '4 weeks ago':
        return datetime.strptime((date.today() - relativedelta(weeks=+4)).strftime('%Y%m%d'), '%Y%m%d')
    elif day == '3 weeks ago':
        return datetime.strptime((date.today() - relativedelta(weeks=+3)).strftime('%Y%m%d'), '%Y%m%d')
    elif day == '2 weeks ago':
        return datetime.strptime((date.today() - relativedelta(weeks=+2)).strftime('%Y%m%d'), '%Y%m%d')
    elif day[2:5] == 'day':
        return datetime.strptime((date.today() - relativedelta(days=+ int(day[0]))).strftime('%Y%m%d'), '%Y%m%d')
    elif (day[2:6] == 'hour') | (day[3:7] == 'hour'):
        return datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d')  
    else:
        return datetime.strptime(day, '%b %d, %Y')


all['date'] = all.date.apply(date_convert)




