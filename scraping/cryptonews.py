from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time

def cryptonews_scrape(entity, start_date, end_date): 
    # remove notifications
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # create driver
    driver = webdriver.Chrome('./utils/chromedriver', options=chrome_options)

    entity_name = entity.replace(" ", "+")

    # search for webpage
    search = "https://cryptonews.com/search/articles.htm?q=" + entity_name
    driver.get(search)

    # preliminary search of all articles
    articles = driver.find_elements_by_xpath("//div[@class='cn-tile article']")

    column_names = ["date_time", "title", "category", "article_url"]
    df = pd.DataFrame(columns = column_names)

    if len(articles) > 0:

        soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

        # time
        date_string = soup.find("time")["datetime"][:-6]
        date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

        # keep pressing load more button until reach start date
        current_date = date_time
        while current_date >= start_date:
            try:
                # refind load button and press
                load_more_section = driver.find_element_by_xpath("//div[@class='cn-section-controls']")
                load_more_button = load_more_section.find_element_by_tag_name("a")
                action = ActionChains(driver)
                action.move_to_element(load_more_button).click(load_more_button).perform()
                time.sleep(3)
            except:
                # no more load more button
                pass
                break

            # retrieve articles again
            articles = driver.find_elements_by_xpath("//div[@class='cn-tile article']")
            soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

            # retrieve earliest date
            date_string = soup.find("time")["datetime"][:-6]
            date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

            current_date = date_time

        # retrieve details from all articles
        for article in articles: 
            soup = BeautifulSoup(article.get_attribute("innerHTML"), features="html.parser")

            # retrieve date
            date_string = soup.find("time")["datetime"][:-6]
            date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

            if date_time > end_date:
                continue

            # retrieve url and text
            article_module = soup.find("h4")
            article_url = "https://cryptonews.com" + article_module.find("a")["href"]
            title_text = article_module.text

            # retrieve category
            category = soup.find("span", class_='notch').find("a").text

            # add information to dataframe
            df = df.append({"date_time": date_time, "title": title_text, \
                "category": category, "article_url": article_url}, ignore_index=True)

    driver.quit()
    return df

# entity = "Forsage.io"
# start_date = datetime(2020, 7, 17)
# end_date = datetime(2020, 8, 10)
# df = cryptonews_scrape(entity, start_date, end_date)
# print(df)
