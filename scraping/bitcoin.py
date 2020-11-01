# importing packages
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

def bitcoin_scrape(entity, start_date, end_date):
    # create output df
    column_names = ['date_time', 'title', 'excerpt', 'article_url', 'image_url', 'category']
    output = pd.DataFrame(columns = column_names)

    page_number = 1
    continue_search = True

    # continue_search = False when date_time < start_date
    while continue_search:
        # retrieve HTML content
        html = requests.get("https://news.bitcoin.com/page/{}/?s={}".format(page_number, entity))
        html_content = html.content

        # locate relevant sections
        soup = BeautifulSoup(html_content, 'html.parser')
        news = soup.find_all('div', class_='td_module_16 td_module_wrap td-animation-stack')
        news_details = soup.find_all('div', class_='td-module-meta-info')
        news_excerpt = soup.find_all('div', class_='td-excerpt')

        # loop through all articles on the page
        for i in range(0, len(news)):
            # retrieve relevant attributes
            # note datetime string is in the format '2020-06-01T14:04:01+00:00'
            date_time_str = news[i].find('time')['datetime'][0:10]
            date_time = datetime.strptime(date_time_str, '%Y-%m-%d')
            title = news[i].find('a')['title']
            article_url = news[i].find('a')['href']
            image_url = news[i].find('img')['src']
            excerpt = news_excerpt[i].get_text()
            try: 
                category = news_details[i].find('a').get_text()
            except:
                category = ''
                pass

            # check whether datetime is wihin range
            if (date_time <= end_date) and (date_time >= start_date):
                # append row to data frame
                output = output.append({'date_time': date_time, 'title': title, 'excerpt': excerpt, \
                                        'article_url': article_url, 'image_url': image_url, \
                                        'category': category}, ignore_index=True)
            
            # terminating conditions
            if (date_time < start_date):
                continue_search = False
        
        # break loop if no search results
        if len(news) == 0:
            break
        
        # increment page number
        page_number += 1
    
    return output

# testing function
# start_date = datetime(2020, 8, 20)
# end_date = datetime(2020, 8, 30)
# test = bitcoin_scrape("bitcoin", start_date, end_date)
# print(test)