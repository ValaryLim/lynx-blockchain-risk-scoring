""" 
Articles on newsbtc are not sorted by date 
and hence excluded from scraping. 
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
from datetime import datetime

def newsbtc_scrape(entity, start_date, end_date):    
    # remove all ' ' characters in url
    entity = entity.replace(' ','+')
    
    # storing required data
    data = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}
    
    # retrieve max page number    
    url = 'https://www.newsbtc.com/page/1/?s='+ entity
    page = requests.get(url).text
    soup = BeautifulSoup(page, 'html.parser')
   
    max_page = 1
    res1 = soup.find('div',class_ = 'jeg_navigation jeg_pagination jeg_pagenav_2 jeg_aligncenter no_navtext no_pageinfo')
    if res1 != None:
        for i in res1.find_all('a', class_= 'page_number'):
            max_page = int(i.text)
    
    # iterate through all the pages
    for i in range(1,max_page+1): 
        url = 'https://www.newsbtc.com/page/' + str(i) +'/?s='+ entity
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
       
        for res in soup.find_all('article'):
            article_url = res.h3.a['href']
            
            # retrieve date of article
            split_url = article_url.split("/")
            try:
                int(split_url[3])
                date_time = split_url[3] + "/" + split_url[4] + "/" + split_url[5]
                d = datetime.strptime(date_time, '%Y/%m/%d')   
            except ValueError:
                continue
            
            # if current date is within time frame, retrieve all info and store in dataframe
            if d <= end_date and d >= start_date:
                data['date_time'].append(d)    
                data['article_url'].append(article_url)

                title = res.h3.a.text.lower()
                data['title'].append(title)

                description = res.find('div', class_ = 'jeg_post_excerpt').p.text.lower()
                data['excerpt'].append(description)

                image_url = res.find('div', class_= 'jeg_thumb').img.get('data-src')
                data['image_url'].append(image_url)

                author_a = res.find('div', class_ = 'jeg_meta_author')
                author = author_a.a.text
                data['author'].append(author)

                author_url = author_a.a.get('href')
                data['author_url'].append(author_url)
                
    # return dataframe of data     
    df = pd.DataFrame(data)
    return df

# test
# entity = 'binance'
# start_date = datetime(2020, 7, 1)
# end_date = datetime(2020, 9, 1)
# test = newsbtc_scrape(entity, start_date, end_date)
