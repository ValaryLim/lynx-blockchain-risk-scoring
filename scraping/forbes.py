from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import numpy as np

def forbes_scrape(entity, start_date, end_date):  
    # remove all ' ' characters in url
    entity = entity.replace(' ','+')

    # store data
    data = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[], 'source_id': []}

    page_num = 0
    last_date = end_date

    # iterate through all the pages there are 
    while last_date >= start_date:
        start_page = page_num*20

        url = 'https://www.forbes.com/simple-data/search/more/?start=' + str(start_page) + '&sort=recent&q=' + entity
        page = requests.get(url).text
        soup = BeautifulSoup(page, 'html.parser')
        
        results = soup.find_all('article')

        if results == []:
            break
        else:
            for res in results:
                # get the date of the article
                timestamp_info = res.find('div', class_ = 'stream-item__date')
                timestamp = int(timestamp_info['data-date'])
                date_time = datetime.fromtimestamp(timestamp/1000)  
                last_date = date_time # update current date

                if date_time <= end_date and date_time >= start_date:
                    # store info in dataframe if it lies in the date range 
                    title_info = res.find("a", class_ = "stream-item__title")
                    title = title_info.text
                    data['title'].append(title)

                    article_url = title_info["href"]

                    data['article_url'].append(article_url)

                    description = res.find("div", "stream-item__description").text
                    data['excerpt'].append(description)

                    author_info = res.find("a", "byline__author-name")
                    author = author_info.text
                    data['author'].append(author)

                    author_url = author_info["href"]
                    data['author_url'].append(author_url)

                    data['date_time'].append(date_time)

                    data['image_url'] = ''

                    source_id = res["data-id"]
                    data['source_id'].append(source_id)

            page_num += 1

    df = pd.DataFrame(data)
    return df


############### Testing ################
# entity = 'binance'
# start_date = datetime(2020,6, 3)
# end_date = datetime(2020,8, 30, 23, 59, 59)
# df = forbes_scrape(entity, start_date, end_date)
######################################
