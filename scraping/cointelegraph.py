from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import json

def cointelegraph_scrape(entity, start_date, end_date):  
    # remove all ' ' characters in url
    entity = entity.replace(' ','+')

    # store data
    data = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[], 'source_id': []}

    # retrieve data from url
    url = 'https://cointelegraph.com/search?query=' + entity
    req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(req, 'html.parser')
    token = soup.find("meta",  attrs={'name':"csrf-token"})['content']
    
    # helper function to retrieve data by entity and page number
    def retrieve_data(entity, page_num, token):
        # retrieve data from cointelegraph API
        r = requests.post("https://cointelegraph.com/api/v1/content/search/result", \
                          params = dict(query=entity,
                                        page=page_num,
                                        _token =token), \
                          headers={'User-Agent': 'Mozilla/5.0'})
        # get results in json format
        results = r.json()
        return results['posts']
        
    page_num = 1
    page_data = retrieve_data(entity, page_num, token)

    # retrieve datetime for the last submission in the page
    last = end_date

    while last >= start_date:
        # stop if there are no search results
        if page_data == []:
            break

        else:
            for article in page_data:
                if article == None:
                    continue
                else:
                    date_time =  datetime.strptime(article['published']["date"], "%Y-%m-%d %H:%M:%S.000000")
                    last = date_time

                    # retrieve article information if it is within specified data range
                    if date_time <= end_date and date_time >= start_date: 
                        data['date_time'].append(date_time)

                        title = article['title']
                        data['title'].append(title)
                    
                        excerpt = article['lead']
                        data['excerpt'].append(excerpt)

                        article_url = article['url']
                        data['article_url'].append(article_url)

                        author_url = article['author_url']
                        data['author_url'].append(author_url)

                        author = article['author_title']
                        data['author'].append(author)

                        image = article['retina']
                        data['image_url'].append(image)

                        source_id = article['id']
                        data['source_id'].append(source_id)

            # scrape next page
            page_num += 1
            page_data = retrieve_data(entity, page_num, token)

    df = pd.DataFrame(data)
    return df
    

# ############### testing ################
# entity = 'Etheremon'
# start_date = datetime(2020, 8, 1)
# end_date = datetime(2020, 10, 25, 23, 59, 59)
# df = cointelegraph_scrape(entity, start_date, end_date)
# ######################################
