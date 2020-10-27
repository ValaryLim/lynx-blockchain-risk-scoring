from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import json

def cointelegraph_scrape(entity, start_date, end_date):  
    #Remove all ' ' characters in url
    entity = entity.replace(' ','+')

    #Store data
    data = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}

    #retrieve 
    url = 'https://cointelegraph.com/search?query=' + entity
    req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}).text
    soup = BeautifulSoup(req, 'html.parser')
    token = soup.find("meta",  attrs={'name':"csrf-token"})['content']
    

    #Request and get url
    def retrieve_data(entity, page_num, token):
        #Link to retrieve data from
        r = requests.post("https://cointelegraph.com/api/v1/content/search/result", params=dict(
        query=entity,
        page=page_num,
        _token =token
        ), headers={'User-Agent': 'Mozilla/5.0'})

        results = r.json()
        return results['posts']
        
    
    page_num = 1
    page_data = retrieve_data(entity, page_num, token)

    #Retrieve datetime for the last submission in the page
    last = end_date

    while last >= start_date:
        
        if page_data == []:
            break
        else:
            for article in page_data:
                if article == None:
                    continue
                else:
                    date_time =  datetime.strptime(article['published']["date"], "%Y-%m-%d %H:%M:%S.000000")
                    last = date_time

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
                
            page_num += 1
            page_data = retrieve_data(entity, page_num, token)

    df = pd.DataFrame(data)
    return df
    



# ###############Testing################
# entity = 'Etheremon'
# start_date = datetime(2020, 8, 1)
# end_date = datetime(2020, 10, 25, 23, 59, 59)
# df = cointelegraph_scrape(entity, start_date, end_date)
# ######################################
