from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pandas as pd
import numpy as np
import json

def cryptonews_scrape(entity, start_date, end_date):  
    #Remove all ' ' characters in url
    entity = entity.replace(' ','+')

    #Store data
    data = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}
    

    #Get the html data using the post method
    def retrieve_data(entity, offset_num):

        #Link to retrieve data from
        r = requests.post("https://cryptonews.com/search/", json=json.dumps(dict(
        q=entity, # checked on this, the entity filtering is working fine
        event= 'sys.search#morepages',
        where= 'YToyOntpOjA7czo4OiJhcnRpY2xlcyI7aToxO3M6NzoiYmluYW5jZSI7fQ==',
        offset= offset_num, # +48 each time.  NOT WORKING
        articles_type='undefined',
        pages = 3, 
        )), headers={'User-Agent': 'Mozilla/5.0'})

        page = r.text
        soup = BeautifulSoup(page, 'html.parser')
        results = soup.find_all("div", {"class": "cn-tile article"})
        return results

    offset_num = 0
    page_data = retrieve_data(entity, offset_num)

    #The last variable tracks the date_time of most recent article retrieved
    last = end_date

    while last >= start_date:    
        #print(results)

        if page_data == []:
            break
        else:
            for article in page_data:

                #Get the date of the article
                date_string = article.find("time")["datetime"][:-6]
                date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S") 
                print("datetime of article ", date_time)

                last = date_time # update current date
            
                if date_time <= end_date and date_time >= start_date:
                    ## Store info in dataframe if it lies in the date range
                    data['date_time'].append(date_time)

                    # retrieve url and text
                    article_module = article.find("h4")
                    article_url = "https://cryptonews.com" + article_module.find("a")["href"]
                    title_text = article_module.text
                    data['title'].append(title_text)
                    print("title of article ", title_text)
                    data['excerpt'].append("")
                    data['article_url'].append(article_url)

                    # retrieve img url
                    img_url = article.find("img")["src"]
                    data['image_url'].append(img_url)

                    # no author info
                    data['author'].append("")
                    data['author_url'].append("")
        
            print("=============================")
            print("current offset ",  offset_num)
            #print(data['title'])
            offset_num += 48 #referred to inspect on chrome
            page_data = retrieve_data(entity, offset_num)

    df = pd.DataFrame(data)
    return df

# ###############Testing################
entity = 'binance'
start_date = datetime(2020, 10, 1)
end_date = datetime(2020, 10, 28)
df = cryptonews_scrape(entity, start_date, end_date)
# ######################################
