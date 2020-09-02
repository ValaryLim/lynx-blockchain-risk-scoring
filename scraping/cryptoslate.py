from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import time

def cryptoslate_scrape(entity, start_date, end_date): 
    # create driver
    driver = webdriver.Chrome('./utils/chromedriver')

    # search for webpage
    url = "https://cryptoslate.com/?s={}".format(entity)
    driver.get(url)

    # preliminary search of all articles
    articles = driver.find_elements_by_xpath("//div[@class='list-post-excerpt clearfix ']")

    # retrieve last article (least recent)
    soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

    # retrieve url of last article
    last_url = soup.find("a")["href"]
    # click on url
    html = requests.get(last_url)
    html_content = html.content
    soup = BeautifulSoup(html_content)
    # retrieve date of last article
    full_date = soup.find_all('span', class_='post-date')[0].get_text()
    date_string = full_date.split("at", 1)[0]
    date_time = datetime.strptime(date_string, "%B %d, %Y ")

    # keep pressing load more button until reach start date
    current_date = date_time
    while current_date >= start_date:
        # refind load button and press
        load_more_button = driver.find_element_by_xpath("//a[@class='load-more news-load-more-ajax']")
        action = ActionChains(driver)
        action.move_to_element(load_more_button).click(load_more_button).perform()
        time.sleep(3)

        # retrieve articles again
        articles = driver.find_elements_by_xpath("//div[@class='list-post-excerpt clearfix ']")
        soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

        # retrieve earliest date
        last_url = soup.find("a")["href"]
        # click on url
        html = requests.get(last_url)
        html_content = html.content
        soup = BeautifulSoup(html_content)
        # retrieve date of last article
        full_date = soup.find_all('span', class_='post-date')[0].get_text()
        date_string = full_date.split("at", 1)[0]
        date_time = datetime.strptime(date_string, "%B %d, %Y ")

        # update current_date
        current_date = date_time
    
    # create output dataframe
    column_names = ["title", "excerpt", "article_url", "author"]
    df = pd.DataFrame(columns = column_names)

    # retrieve details from all articles
    for article in articles:
        soup = BeautifulSoup(article.get_attribute("innerHTML"), features="html.parser")

        # retrieve title and article_url
        article_details = soup.find('article').find('a')
        title = article_details['title']
        article_url = article_details['href']

        # retrieve excerpt
        excerpt = article_details.find('p').get_text()

        # retrieve author
        author = article_details.find('div', class_='post-meta').get_text()
        # slice to retrieve author part of string
        author = author.split("·")[0]
        # remove leading and trailing whitespaces
        author = author.strip()

        # add information to dataframe
        df = df.append({"title": title, "excerpt": excerpt, \
                        "article_url": article_url, "author": author}, ignore_index=True)

    driver.quit()

    datetime_lst = []

    # loop through df
    for i in range(len(df)):
        # retrieve url
        article_url = df.iloc[i]['article_url']
        # retrieve date from url
        html = requests.get(article_url)
        html_content = html.content
        soup = BeautifulSoup(html_content)
        full_date = soup.find_all('span', class_='post-date')[0].get_text()
        date_string = full_date.split("at", 1)[0]
        date_time = datetime.strptime(date_string, "%B %d, %Y ")
        datetime_lst.append(date_time)
    
    # add date_time column to df
    df['date_time'] = datetime_lst

    return df

# testing function
# start_date = datetime(2020, 8, 24)
# end_date = datetime(2020, 8, 26)
# test = cryptoslate_scrape("bitcoin", start_date, end_date)
# print(test)