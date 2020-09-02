import pandas as pd
from GoogleNews import GoogleNews
from datetime import datetime, date
import regex as re
from dateutil.relativedelta import *


def google_scrap(entity, start_date, end_date):
    
    '''
    Scrap (using GoogleNews API) the top 10 headlines of google news on a particular entity, for a given time range
    Output : Pandas Dataframe with title, short summary, date & url column
    '''
    news = GoogleNews(start=start_date.strftime("%m/%d/%Y"),end=end_date.strftime("%m/%d/%Y"), lang='en', encode='utf-8')
    news.search(f"{entity}")   # Main bulk of time, taking ~2 seconds to search
    
    if pd.DataFrame(news.result()).empty:
        # No relevant articles 
        return pd.DataFrame(columns=['date_time', 'title', 'excerpt', 'article_url'])
    
    df = pd.DataFrame(news.result())[['title', 'desc', 'date', 'link']]
    # Rename columns
    df.columns = ['title', 'excerpt', 'date_time', 'article_url']
    
    # Only get headlines which mention the entity of interest
    df=df[df['title'].str.contains(entity,flags=re.IGNORECASE)].reset_index(drop=True)
    df['date_time'] = df.date_time.apply(date_convert)
    
    # Reorder columns
    df=df[['date_time', 'title', 'excerpt', 'article_url']]
    
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
        return datetime.strptime(day, '%b %d, %Y')

# start_date = datetime(2020, 7, 27)
# end_date = datetime(2020, 9, 1)
# test = google_scrap("Binance", start_date, end_date)
# print(test)






