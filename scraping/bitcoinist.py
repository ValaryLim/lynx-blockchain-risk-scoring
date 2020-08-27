from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import requests
import time

def bitcoinist_scrape(entity, start_date, end_date): 
    # create driver
    driver = webdriver.Chrome('./utils/chromedriver')

    # search for webpage
    url = "https://bitcoinist.com/?s={}&lang=en".format('bitcoin')
    driver.get(url)

    # preliminary search of all articles
    articles = driver.find_elements_by_xpath("//div[@class='news three columns wo-gutter grid-medium  ']")

    # retrieve last article (least recent)
    soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

    # retrieve url of last article
    last_url = soup.find("h3").find("a")["href"]
    # click on url
    html = requests.get(last_url)
    html_content = html.content
    soup = BeautifulSoup(html_content)
    # retrieve date of last article
    article_header = soup.find('div', class_='hero-mobile mobile')
    article_text = article_header.find('p').get_text()
    date_string = article_text.split("|")[1].strip()
    date_time = datetime.strptime(date_string, "%b %d, %Y")

    # keep pressing load more button until reach start date
    current_date = date_time
    while current_date >= start_date:
        # refind load button and press
        load_more_button = driver.find_element_by_xpath("//div[@class='infinite-scroll--load-more load-more-btn']")
        action = ActionChains(driver)
        action.move_to_element(load_more_button).click(load_more_button).perform()
        time.sleep(3)

        # retrieve articles again
        articles = driver.find_elements_by_xpath("//div[@class='news three columns wo-gutter grid-medium  ']")
        soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

        # retrieve earliest date
        last_url = soup.find("h3").find("a")["href"]
        # click on url
        html = requests.get(last_url)
        html_content = html.content
        soup = BeautifulSoup(html_content)
        # retrieve date of last article
        article_header = soup.find('div', class_='hero-mobile mobile')
        article_text = article_header.find('p').get_text()
        date_string = article_text.split("|")[1].strip()
        date_time = datetime.strptime(date_string, "%b %d, %Y")

        # update current_date
        current_date = date_time
    
    # create output dataframe
    column_names = ["title", "excerpt", "article_url", "image_url", "author", "author_url", "category"]
    df = pd.DataFrame(columns = column_names)

    # retrieve details from all articles
    for article in articles:
        soup = BeautifulSoup(article.get_attribute("innerHTML"), features="html.parser")

        # retrieve title and article_url
        article_details = soup.find('div', class_='news-content cf')
        article_header = article_details.find('h3', class_='title').find('a')
        title = article_header.get_text()
        article_url = article_header['href']

        # retrieve excerpt
        excerpt = article_details.find('p', class_='excerpt').get_text()

        # retrieve author and author url
        author_details = article_details.find('span', class_='meta').find('span', class_='author').find('a')
        author = author_details.get_text()
        author_url = author_details['href']

        # retrieve category
        category = article_details.find('a', class_='category').get_text()

        # retrieve image url
        image_url = soup.find('img')['src']

        # add information to dataframe
        df = df.append({"title": title, "excerpt": excerpt, "article_url": article_url, \
                        "image_url": image_url, "author": author, "author_url": author_url, \
                        "category": category}, ignore_index=True)

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
        article_header = soup.find('div', class_='hero-mobile mobile')
        article_text = article_header.find('p').get_text()
        date_string = article_text.split("|")[1].strip()
        date_time = datetime.strptime(date_string, "%b %d, %Y")
        datetime_lst.append(date_time)

    # add date_time column to df
    df['date_time'] = datetime_lst

    # filter by date
    df_filtered = df.loc[df['date_time'] >= start_date]
    df_filtered = df_filtered.loc[df['date_time'] <= end_date]

    return df_filtered

# testing function
# start_date = datetime(2020, 8, 25)
# end_date = datetime(2020, 8, 26)
# test = bitcoinist_scrape("bitcoin", start_date, end_date)
# print(test)