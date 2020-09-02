import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime, date
import regex as re
from dateutil.relativedelta import *


def google_scrape(entity, start_date, end_date):
    
    '''
    Scrap (using GoogleNews API) the top 10 headlines of google news on a particular entity, for a given time range
    Output : Pandas Dataframe with title, short summary, date & url column
    '''
    news = GoogleNews(start=start_date.strftime("%m/%d/%Y"),end=end_date.strftime("%m/%d/%Y"), lang='en', encode='utf-8')
    news.search(f"{entity}")   # Main bulk of time, taking ~2 seconds to search
    
    if pd.DataFrame(news.result()).empty:
        # No relevant articles 
        return pd.DataFrame(columns=['date_time', 'title', 'excerpt', 'article_url'])
    
    df = pd.DataFrame(news.result())[['date', 'title', 'desc', 'media', 'link']]
    # Rename columns
    df.columns = ['date_time', 'title', 'excerpt', 'domain', 'article_url']
    
    # Only get headlines which mention the entity of interest
    df=df[df['title'].str.contains(entity,flags=re.IGNORECASE)].reset_index(drop=True)
    df['date_time'] = df.date_time.apply(date_convert)

    # remove rows without datetime
    df = df.dropna(axis=0, subset=["date_time"])
    
    return df


def date_convert(day): 
    if day == '1 month ago':
        return datetime.strptime((date.today() - relativedelta(months=+1)).strftime('%Y%m%d'), '%Y%m%d')
    elif day[2:6] == 'week':
        return datetime.strptime((date.today() - relativedelta(weeks=+ int(day[0]))).strftime('%Y%m%d'), '%Y%m%d')
    elif day[2:5] == 'day':
        return datetime.strptime((date.today() - relativedelta(days=+ int(day[0]))).strftime('%Y%m%d'), '%Y%m%d')
    elif (day[2:6] == 'hour') | (day[3:7] == 'hour'):
        return datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d')  
    else:
        try:
            return datetime.strptime(day, '%b %d, %Y')
        except:
            return None

# start_date = datetime(2018, 5, 22, 0, 0, 0)
# end_date = datetime(2018, 5, 23, 23, 59, 59)
# test = google_scrape("Ethereum", start_date, end_date)
# print(test)

