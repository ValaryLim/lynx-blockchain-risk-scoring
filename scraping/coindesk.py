import pandas as pd
import requests
from datetime import datetime
import time

def coindesk_scrape(entity, start_date, end_date):

    # dictionary to store the relevant data
    data_store = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[],  'author':[], 'image_url':[]}

    # request and get url
    def retrieve_data(entity, page):
        # link to retrieve data from
        url = 'https://www.coindesk.com/wp-json/v1/search?keyword=' + str(entity) + '&page=' + str(page)
        data = requests.get(url).json()
        return data['results']

    page = 1
    page_data = retrieve_data(entity, page)

    # retrieve datetime for the last submission in the page
    last = end_date

    while last >= start_date:
        # if there are no search results, stop
        if page_data == []:
            break
        else:
            for article in page_data:
                date_time =  datetime.strptime(article['date'], "%Y-%m-%dT%H:%M:%S")
                last = date_time

                # retrieve relevant information from article
                if date_time <= end_date and date_time >= start_date: 
                    data_store['date_time'].append(date_time)

                    title = article['title']
                    data_store['title'].append(title)
                
                    excerpt = article['text']
                    data_store['excerpt'].append(excerpt)

                    article_url = article['url']
                    article_url = article_url.replace("\\", "")
                    data_store['article_url'].append(article_url)

                    author = article['author'][0]['name']
                    data_store['author'].append(author)

                    # try except block for articles without image url
                    try:
                        image = article['images']['images']['desktop']['src']
                        data_store['image_url'].append(image)
                    except:
                        data_store['image_url'].append('')
            
            # increment page number
            page += 1
            page_data = retrieve_data(entity, page)

    df = pd.DataFrame(data_store)
    return df


############### Testing ################
# entity = 'binance'
# start_date = datetime(2020, 7, 28)
# end_date = datetime(2020, 9, 20,23,59,59)
# df = coindesk_scrape(entity, start_date, end_date)
# ######################################
