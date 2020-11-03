from bs4 import BeautifulSoup
import requests
from datetime import datetime
import datetime as dt
import pandas as pd
import numpy as np

def cryptoslate_scrape(entity, start_date, end_date):  
    #Remove all ' ' characters in url
    entity = entity.replace(' ','+')

    #Store data
    data = {'source_id':[], 'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}
    

    #Request and get url
    def retrieve_data(entity, offset_num):

        #Link to retrieve data from
        r = requests.post("https://cryptoslate.com/wp-admin/admin-ajax.php", data=dict(
            action='ajax_news_search',
            searchTerm=entity,
            offset= offset_num, # +10 each time
        ))

        page = r.json()["posts"]
        soup = BeautifulSoup(page, 'html.parser')
        results = soup.find_all("div", {"class": 'list-post-excerpt clearfix'})
        return results

    offset_num = 0
    page_data = retrieve_data(entity, offset_num)

    #Retrieve datetime for the last submission in the page
    last = end_date

    while last >= start_date:    

        if page_data == []:
            break
        else:
            for article in page_data:

                #Get the date of the article
                date_info = article.find("div", {"class": "post-meta"}).text.split("·")[1]

                if date_info.find("min") != -1:
                    date_time = datetime.now() - dt.timedelta(minutes=int(date_info.split(" ")[1]))
                elif date_info.find("hour") != -1:
                    date_time = datetime.now() - dt.timedelta(hours=int(date_info.split(" ")[1]))
                elif date_info.find("day") != -1:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[1]))
                elif date_info.find("week") != -1:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[1])*7)
                elif date_info.find("month") != -1:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[1])*30)
                else:
                    date_time = datetime.now() - dt.timedelta(days=int(date_info.split(" ")[1])*30*12)

                last = date_time # update current date

                if date_time <= end_date and date_time >= start_date:
                    ## Store info in dataframe if it lies in the date range
                    data['date_time'].append(date_time)
                    #print("article time ", date_time)

                    # retrieve article id
                    article_id = article.find('article')['id']
                    data['source_id'].append(article_id)

                    # retrieve url and text
                    article_details = article.find('article').find('a')
                    title_text = article_details['title']
                    article_url = article_details['href']
                    data['title'].append(title_text)
                    data['article_url'].append(article_url)

                    # retrieve excerpt
                    excerpt = article.find('p').get_text()
                    data['excerpt'].append(excerpt)

                    data['image_url'].append("")

                    # retrieve author
                    author = article_details.find('div', class_='post-meta').get_text()
                    author = author.split("·")[0]
                    author = author.strip()
                    data['author'].append(author)
                    data['author_url'].append("")

            offset_num += 10 # increase offset to retrieve more data
            page_data = retrieve_data(entity, offset_num)

    df = pd.DataFrame(data)
    return df
    



# ###############Testing################
# entity = 'binance'
# start_date = datetime(2020, 5, 1)
# end_date = datetime(2020, 10, 28)
# df = cryptoslate_scrape(entity, start_date, end_date)
# df.to_csv("temp.csv")
# ######################################
