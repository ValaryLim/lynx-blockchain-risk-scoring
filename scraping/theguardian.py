import json
import requests
from datetime import datetime
import pandas as pd

def theguardian_scrape(entity, start_date, end_date):
    # set search parameters
    search_api_url = "http://content.guardianapis.com/search"
    search_params = {
        "q": entity,
        "from-date": start_date.strftime("%Y-%m-%d"),
        "to-date": end_date.strftime("%Y-%m-%d"),
        "order-by": "newest",
        "show-fields": "all",
        "page-size": 200,
        "api-key": "0c96df6a-0f51-4263-8013-274156d8db83"
    }

    # retrieve results
    page_num = 1
    total_pages = 1
    all_results = []

    while page_num <= total_pages:
        search_params["page"] = page_num
        page = requests.get(search_api_url, search_params)
        data = page.json()
        all_results.extend(data['response']['results'])
        
        # if there is more than one page
        page_num += 1
        total_pages = data['response']['pages']
    
    # parse results into dataframe
    column_names = ["date_time", "title", "excerpt", "article_url"]
    df = pd.DataFrame(columns = column_names)

    for result in all_results:
        # retrieve date
        date_string = result["webPublicationDate"]
        date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

        # retrieve title
        title_text = result["webTitle"]
        article_url = result["webUrl"]

        # retrieve excerpt
        excerpt = result["fields"]["bodyText"]

        # add information to dataframe when entity is in text (self-filter)
        if entity in title_text or entity in excerpt:
            df = df.append({"date_time": date_time, "title": title_text, \
                    "excerpt": excerpt, "article_url": article_url
                }, ignore_index=True)
    
    return df

# entity = "ethereum"
# start_date = datetime(2019, 1, 17)
# end_date = datetime(2020, 8, 17)
# df = theguardian_scrape(entity, start_date, end_date)
# print(df)