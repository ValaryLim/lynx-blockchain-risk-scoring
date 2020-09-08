from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import date
import pandas as pd
import time


def cointelegraph_scrape(entity, start_date, end_date): 
    # remove notifications
    chrome_options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications" : 2}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # create driver
    driver = webdriver.Chrome('./utils/chromedriver', options=chrome_options)

    # search for webpage
    search = f"https://cointelegraph.com/search?query={entity}"
    driver.get(search)

    driver.implicitly_wait(5)
    # press accept cookies
    driver.find_element_by_xpath("//div[@class='privacy-policy__col privacy-policy__col_btn']/button").click()

    # preliminary search of all articles
    articles = driver.find_elements_by_xpath("//div[@class='row result']")
    time.sleep(3)

    column_names = ["date_time", "title", "excerpt", "article_url", "category"]
    df = pd.DataFrame(columns = column_names)

    if len(articles) > 1:
        soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

        # time
        date_string = soup.find(class_="date").text
        if(date_string.split(" ")[2]=="AGO"):   # deals with 'X HOURS AGO' format
            date_time = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d')
        else:
            date_time = datetime.strptime(date_string, "%b %d, %Y")

        # keep pressing load more button until reach start date
        current_date = date_time
        while current_date >= start_date:
            try:
                # refind load button and press
                # driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                # time.sleep(2)
                load_more_section = driver.find_element_by_xpath("//div[@class='col-xs-12 load']")
                load_more_button = load_more_section.find_element_by_tag_name("a")
                action = ActionChains(driver)
                action.move_to_element(load_more_button).click(load_more_button).perform()
                time.sleep(10)
            except:
                # no more load button
                break

            # retrieve articles again
            articles = driver.find_elements_by_xpath("//div[@class='row result']")
            soup = BeautifulSoup(articles[-1].get_attribute("innerHTML"), features="html.parser")

            # retrieve earliest date
            date_string = soup.find(class_="date").text
            if(date_string.split(" ")[2]=="AGO"):   # deals with 'X HOURS AGO' format
                date_time = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d')
            else:
                date_time = datetime.strptime(date_string, "%b %d, %Y")

            current_date = date_time   

        # retrieve details from all articles
        for article in articles: 
            soup = BeautifulSoup(article.get_attribute("innerHTML"), features="html.parser")

            # retrieve date
            date_string = soup.find(class_="date").text
            if(date_string.split(" ")[2]=="AGO"):
                date_time = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d')
            else:
                date_time = datetime.strptime(date_string, "%b %d, %Y")

            if date_time > end_date:
                continue

            if date_time < start_date:
                break

            # retrieve url and text 
            article_module = soup.find(class_="header").find("a")
            article_url = article_module["href"]
            title_text = article_module.text.strip()
            
            # retrieve excerpt
            excerpt = soup.find(class_="text").find("a").text.strip()

            # retrieve category
            category = soup.find(class_="image").find("p").text

            # add information to dataframe
            df = df.append({"date_time": date_time, "title": title_text, "excerpt": excerpt, "article_url": article_url, "category": category}, ignore_index=True)

    driver.quit()
    return df


## testing function
# start_date = datetime(2020, 8, 20)
# end_date = datetime(2020, 8, 28)
# test = cointelegraph_scrape("bitcoin", start_date, end_date)