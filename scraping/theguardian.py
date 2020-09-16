import json
import requests
from datetime import datetime
import pandas as pd

def theguardian_scrape(entity, start_date, end_date):
    # get api key
    with open('api_key.json') as f:
        api_key = json.load(f)['theguardian']
        
    # set search parameters
    search_api_url = "http://content.guardianapis.com/search"
    search_params = {
        "q": entity,
        "from-date": start_date.strftime("%Y-%m-%d"),
        "to-date": end_date.strftime("%Y-%m-%d"),
        "order-by": "newest",
        "show-fields": "all",
        "page-size": 200,
        "api-key": api_key
    }

    # retrieve results
    page_num = 1
    total_pages = 1
    all_results = []

    column_names = ["date_time", "title", "excerpt", "article_url"]
    df = pd.DataFrame(columns = column_names)

    try:
        while page_num <= total_pages:
            search_params["page"] = page_num
            page = requests.get(search_api_url, search_params)
            data = page.json()
            all_results.extend(data['response']['results'])
            
            # if there is more than one page
            page_num += 1
            total_pages = data['response']['pages']
    except:
        return df # empty dataframe
    
    # parse results into dataframe
    for result in all_results:
        try:
            # retrieve date
            date_string = result["webPublicationDate"]
            date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

            # retrieve title
            title_text = result["webTitle"]
            article_url = result["webUrl"]

            # retrieve excerpt
            excerpt = result["fields"]["bodyText"]

            # add information to dataframe when entity is in text (self-filter)
            if (entity.lower() in title_text.lower()) or (entity.lower() in excerpt.lower()):
                df = df.append({"date_time": date_time, "title": title_text, \
                        "excerpt": excerpt, "article_url": article_url
                    }, ignore_index=True)
        except:
            continue # if error, skip 
    
    return df

# entity = "Wrapped Ether"
# start_date = datetime(2018, 1, 1)
# end_date = datetime(2019, 12, 31)
# df = theguardian_scrape(entity, start_date, end_date)
# print(df)