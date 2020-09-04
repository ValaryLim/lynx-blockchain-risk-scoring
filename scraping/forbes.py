from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import numpy as np
from datetime import datetime
import time


def forbes_scrape(entity, start_date, end_date):
    entity = entity.replace(' ','+')

    driver = webdriver.Chrome('./utils/chromedriver')


    data = {'date_time':[], 'title':[], 'excerpt':[], 'article_url':[], 'author':[], 'author_url':[]}
    url = 'https://www.forbes.com/search/?q='+ entity + '&sort=recent'

    driver.get(url)

    articles = driver.find_elements_by_tag_name("article")

    if len(articles) > 0: 
        #Get the date of the last article
        last_article = articles[-1]
        timestamp_info = last_article.find_element_by_class_name('stream-item__date')
        timestamp = int(timestamp_info.get_attribute('data-date'))
        last_date = datetime.fromtimestamp(timestamp/1000)
        # print(last_date)


        #While date of last article on page is after start_date, loop     
        while last_date >= start_date:
            #try to locate the search more button and click
            try:
                load_more = driver.find_element_by_class_name("search-more")
                load_more.click()
                time.sleep(3)
                articles = driver.find_elements_by_tag_name("article")

                #Get the date of the article
                last_article = articles[-1]
                timestamp_info = last_article.find_element_by_class_name('stream-item__date')
                timestamp = int(timestamp_info.get_attribute('data-date'))
                last_date = datetime.fromtimestamp(timestamp/1000)        

            #If cannot locate search more, stop loop
            except:
                break
                
            

        for res in articles:
            #Get the date of the article
            timestamp_info = res.find_element_by_class_name('stream-item__date')
            timestamp = int(timestamp_info.get_attribute('data-date'))
            date_time = datetime.fromtimestamp(timestamp/1000)    

            #Store info in dataframe if it lies in the date range 
            if (date_time >= start_date and date_time <= end_date):
                title_info = res.find_element_by_class_name("stream-item__title")
                title = title_info.text.lower()
                data['title'].append(title)

                article_url = title_info.get_attribute("href")
                data['article_url'].append(article_url)

                description = res.find_element_by_class_name("stream-item__description").text.lower()
                data['excerpt'].append(description)

                author_info = res.find_element_by_class_name("byline__author-name")
                author = author_info.text.lower()
                data['author'].append(author)

                author_url = author_info.get_attribute("href")
                data['author_url'].append(author_url)

                data['date_time'].append(date_time)

      
    driver.quit()

    #Generate dataframe with relevant data
    df = pd.DataFrame(data)
    
    return df


###############Test###############
##entity = 'bitcoin'
##start_date = datetime(2020,8,20)
##end_date = datetime(2020,8,29)
##df = forbes_scrape(entity, start_date, end_date)
##################################



