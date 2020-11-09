from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import numpy as np

def cryptonews_scrape(entity, start_date, end_date):  
    
    #Remove all ' ' characters in url
    entity = entity.replace(' ','+')

    #Store data
    data = {'source_id':[], 'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}
    

    #Get the html data using the post method
    def retrieve_data(entity, offset_num):
        url = "https://cryptonews.com/search/"

        body = {'q': 'binance',
        'event': 'sys.search#morepages',
        'where': 'YToyOntpOjA7czo4OiJhcnRpY2xlcyI7aToxO3M6NzoiYmluYW5jZSI7fQ==',
        'offset': offset_num,
        'articles_type': 'undefined'}

        r = requests.post(url,  data = body)

        page = r.json()["pages"][0]
        soup = BeautifulSoup(page, 'html.parser')
        results = soup.find_all("div", {"class": "cn-tile article"})

        return results

    offset_num = 0
    page_data = retrieve_data(entity, offset_num)

    #The last variable tracks the date_time of most recent article retrieved
    last = end_date

    while last >= start_date:    

        if page_data == []:
            break
        else:
            for article in page_data:

                #Get the date of the article
                date_string = article.find("time")["datetime"][:-6]
                date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S") 

                last = date_time # update current date
            
                if date_time <= end_date and date_time >= start_date:
                    ## Store info in dataframe if it lies in the date range
                    data['date_time'].append(date_time)
                    #print("article time ", date_time)

                    # retrieve url and text
                    article_module = article.find("h4")
                    article_url = "https://cryptonews.com" + article_module.find("a")["href"]
                    title_text = article_module.text
                    data['title'].append(title_text)
                    data['excerpt'].append("")
                    data['article_url'].append(article_url)
                    data['source_id'].append('') # no article id avaialble

                    # retrieve img url
                    img_url = article.find("img")["src"]
                    data['image_url'].append(img_url)

                    # no author info
                    data['author'].append("")
                    data['author_url'].append("")
        
            offset_num += 48 #referred to inspect on chrome
            page_data = retrieve_data(entity, offset_num)

    df = pd.DataFrame(data)
    return df

# ###############Testing################
# entity = 'binance'
# start_date = datetime(2020, 10, 1)
# end_date = datetime(2020, 10, 28)
# df = cryptonews_scrape(entity, start_date, end_date)
# df.to_csv("temp.csv")
# ######################################
