""" Articles on blockonomi are not sorted by date. """

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def blockonomi_scrape(entity, start_date, end_date):
    website_url = "https://blockonomi.com"
    page_num = 1
    current_date = end_date

    column_names = ["date_time", "title", "excerpt", "author", \
        "article_url", "image_url", "author_url"]
    df = pd.DataFrame(columns = column_names)

    while current_date >= start_date: 
        # new page of queries
        search = website_url + "/page/" + str(page_num) + "/?s=" + entity
        page = requests.get(search)
        soup = BeautifulSoup(page.content, features="html.parser")

        # retrieve only search items
        results = soup.find_all("article")

        for i in range(len(results)): 
            # retrieve date 
            date_string = results[i].find("time", class_="post-date")["datetime"][:-6]
            date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")
            current_date = date_time # update current date 
  
            if date_time > end_date:  # if after cut-off date, skip
                continue
            if date_time < start_date: # if before cut-off date, stop scraping
                break
            
            # retrieve title and article link
            title_module = results[i].find("h2", class_="post-title-alt")
            title_text = title_module.text.strip()
            article_url = title_module.find("a")["href"]

            # retrieve excerpt
            excerpt = results[i].find("div", class_="post-content post-excerpt cf").text.strip()

            # retrieve image link
            image_url = results[i].find("img")["data-lazy-src"]

            # retrieve author and author link
            author_module = results[i].find("span", class_="post-author")
            author = author_module.find("a").text
            author_url = author_module.find("a")["href"]

            # add information to dataframe
            df = df.append({"date_time": date_time, "title": title_text, \
                "excerpt": excerpt, "author": author, \
                    "article_url": article_url, "image_url": image_url, \
                        "author_url": author_url
                }, ignore_index=True)

        page_num += 1 # scrape next page
        
    return df

# entity = "ethereum"
# start_date = datetime(2019, 9, 17)
# end_date = datetime(2020, 9, 1)
# df = blockonomi_scrape(entity, start_date, end_date)
# print(df)