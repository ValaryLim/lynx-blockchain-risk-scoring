from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import time


def coindesk_scrape(entity, start_date, end_date): 
    # remove notifications
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # create driver
    driver = webdriver.Chrome('./utils/chromedriver', options=chrome_options)

    # search for webpage
    website = "https://www.coindesk.com/"
    search = f"{website}search?q={entity}&s=relevant"
    driver.get(search)

    column_names = ["date_time", "title", "excerpt", "article_url",  "category"]
    df = pd.DataFrame(columns = column_names)

    # preliminary search of all articles
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(3)
    articles = driver.find_elements_by_class_name("list-item-wrapper")
    
    try:
        soup = BeautifulSoup(articles[-2].get_attribute("innerHTML"), features="html.parser")
    except:
        driver.quit()
        return df

    # time 1
    date_string = date_string = soup.find("time").text
    date_time = datetime.strptime(date_string, "%b %d, %Y")

    # keep pressing load more button until reach start date
    current_date = date_time
    while current_date >= start_date:
        try: 
            # refind load button and press
            # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            # time.sleep(2)
            load_more_button = driver.find_element_by_xpath("//button[@class='button primary-button primary-button-default']")
            action = ActionChains(driver)
            action.move_to_element(load_more_button).click(load_more_button).perform()
            time.sleep(3)
        except:
            # no more pages to load
            break

        # retrieve articles again
        articles = driver.find_elements_by_class_name("list-item-wrapper")
        soup = BeautifulSoup(articles[-2].get_attribute("innerHTML"), features="html.parser")

        # retrieve earliest date
        date_string = soup.find("time").text
        date_time = datetime.strptime(date_string, "%b %d, %Y")

        current_date = date_time    

    # retrieve details from all articles
    for article in articles[:-1]: 
        soup = BeautifulSoup(article.get_attribute("innerHTML"), features="html.parser")

        # retrieve date
        date_string = soup.find("time").text
        date_time = datetime.strptime(date_string, "%b %d, %Y")

        if date_time > end_date:
            continue

        if date_time < start_date:
            break

        # retrieve category, url, text and excerpt
        article_module = soup.find(class_="text-content")
        category = article_module.find("span").text
        article_url = website + article_module.find("a")["href"]
        title_text = article_module.find("h4").text
        excerpt = article_module.find(class_="card-text").text.strip()

        # add information to dataframe
        df = df.append({"date_time": date_time, "title": title_text, "excerpt": excerpt, "article_url": article_url, "category": category}, ignore_index=True)

    driver.quit()
    return df


# testing function
# start_date = datetime(2020, 8, 27)
# end_date = datetime(2020, 8, 28)
# test = coindesk_scrape("bitcoin", start_date, end_date)