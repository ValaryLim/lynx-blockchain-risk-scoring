from bs4 import BeautifulSoup
import requests
from datetime import datetime
import datetime as dt
import pandas as pd
import numpy as np

def bitcoinist_scrape(entity, start_date, end_date):  
    
    #Remove all ' ' characters in url
    entity = entity.replace(' ','+')

    #Store data
    data = {'source_id':[], 'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}
    
    #Request and get url
    def retrieve_data(entity, page_num):
        #Link to retrieve data from
        r = requests.post("https://bitcoinist.com/wp-admin/admin-ajax.php", data=dict(
        action = 'svecc_infinite_scroll_archive',
        query = entity,  #the attribute has name query[s]
        page=page_num
        ), headers={'User-Agent': 'Mozilla/5.0'})

        page = r.json()["data"]
        soup = BeautifulSoup(page, 'html.parser')
        results = soup.find_all("div", {"class": 'news three columns wo-gutter grid-medium'})
        return results

    page_num = 1
    page_data = retrieve_data(entity, page_num)

    #Retrieve datetime for the last submission in the page
    last = end_date

    while last >= start_date:    

        if page_data == []:
            break
        else:
            for article in page_data:
                
                #Get the date of the article
                date_info = article.find("span", {"class": "time"}).text
                if date_info.find("min") != -1:
                    date_time = datetime.now() - dt.timedelta(minutes=int(date_info.split(" ")[0]))
                elif date_info.find("hour") != -1:
                    date_time = datetime.now() - dt.timedelta(hours=int(date_info.split(" ")[0]))
                elif date_info.find("day") != -1:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[0]))
                elif date_info.find("week") != -1:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[0])*7)
                elif date_info.find("month") != -1:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[0])*30)
                else:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[0])*30*12)

                last = date_time # update current date

                if date_time <= end_date and date_time >= start_date:
                    ## Store info in dataframe if it lies in the date range
                    # print("article time ", date_time)
                    data['date_time'].append(date_time)
                    
                    # retrieve title and article_url
                    article_details = article.find('div', class_='news-content cf')
                    article_header = article_details.find('h3', class_='title').find('a')
                    title = article_header.get_text()
                    article_url = article_header['href']
                    data['title'].append(title)
                    data['article_url'].append(article_url)
                    data['source_id'].append('') # no article id avaialble

                    # retrieve excerpt
                    excerpt = article_details.find('p', class_='excerpt').get_text()
                    data['excerpt'].append(excerpt)
                    
                    # retrieve image url
                    try:
                        image_url = article.find('img')['src']
                    except:
                        image_url = ""
                    data['image_url'].append(image_url)

                    # retrieve author and author url
                    author_details = article_details.find('span', class_='meta').find('span', class_='author').find('a')
                    author = author_details.get_text()
                    author_url = author_details['href']
                    data['author'].append(author)
                    data['author_url'].append(author_url)

            page_num += 1
            page_data = retrieve_data(entity, page_num)

    df = pd.DataFrame(data)
    return df
    


# ###############Testing################
# entity = 'binance'
# start_date = datetime(2020, 10, 26)
# end_date = datetime(2020, 10, 28)
# df = bitcoinist_scrape(entity, start_date, end_date)
# df.to_csv("temp.csv")
# ######################################

    
