import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def nulltx_scrape(entity, start_date, end_date):
    website_url = "https://nulltx.com"
    page_num = 1
    current_date = end_date

    column_names = ["date_time", "title", "excerpt", "author", \
        "article_url", "image_url", "author_url"]
    df = pd.DataFrame(columns = column_names)

    prev_results = ''

    while current_date >= start_date: 
        # new page of queries
        search = website_url + "/page/" + str(page_num) + "/?s=" + entity
        page = requests.get(search)
        soup = BeautifulSoup(page.content, features="html.parser")
        main_content = soup.find(class_="td-main-content")

        try:
            # retrieve only search items
            results = main_content.find_all(class_="td_module_16")
        except:
            break

        if len(results) == 0:
            break

        for i in range(len(results)): 
            # retrieve date 
            date_string = results[i].find("time", class_="entry-date")["datetime"][:-6]
            date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            current_date = date_time # update current date 
  
            if date_time > end_date:  # if after cut-off date, skip
                continue
            if date_time < start_date: # if before cut-off date, stop scraping
                break
            
            # retrieve title and article link
            title_module = results[i].find("h3", class_="td-module-title")
            title_text = title_module.text
            article_url = title_module.find("a")["href"]

            # retrieve excerpt
            excerpt = results[i].find("div", class_="td-excerpt").text.strip()

            # retrieve image link
            image_url = results[i].find("img")["src"]

            # retrieve author and author link
            author_module = results[i].find("span", class_="td-post-author-name")
            author_url = author_module.find("a")["href"]
            author = author_module.text

            # add information to dataframe
            df = df.append({"date_time": date_time, "title": title_text, \
                "excerpt": excerpt, "author": author, \
                    "article_url": article_url, "image_url": image_url, \
                        "author_url": author_url
                }, ignore_index=True)

        page_num += 1 # scrape next page
        
    return df

# test
# entity = "ethereum"
# start_date = datetime(2019, 7, 17)
# end_date = datetime(2020, 8, 17)
# df = nulltx_scrape(entity, start_date, end_date)
# print(df)