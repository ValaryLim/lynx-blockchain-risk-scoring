from crypto_news_api import CryptoControlAPI
from datetime import datetime
import numpy as np
import pandas as pd
import json

def cryptocontrol_scrape(entity):
    with open('api_key.json') as f:
        api_key = json.load(f)['cryptocontrol']

    # connect to CryptoControlAPI
    api = CryptoControlAPI(api_key)

    # connect to a self-hosted proxy server (to improve performance) that points to cryptocontrol.io
    proxyApi = CryptoControlAPI(api_key, "http://cryptocontrol_proxy/api/v1/public")

    # retrieve all recent articles from that entity
    articles = api.getLatestNewsByCoin(entity)

    # create data frame
    column_names = ["date_time", "title", "excerpt", "domain", \
        "article_url", "image_url", "hotness", "activity_hotness"]
    df = pd.DataFrame(columns = column_names)

    for article in articles:
        # retrieve date
        date_string = article["publishedAt"][:-5]
        date_time = datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S")

        # retrive title and description
        title = article["title"]
        excerpt = article["description"].strip()
        hotness = article["hotness"]
        activity_hotness = article["activityHotness"]

        # retrieve domain and urls
        image_url = article["originalImageUrl"]
        domain = article["source"]["name"]
        article_url = article["url"]

        # add information to dataframe
        df = df.append({"date_time": date_time, "title": title, \
            "excerpt": excerpt, "article_url": article_url, \
                "image_url": image_url, "hotness": hotness, \
                    "activity_hotness": activity_hotness
            }, ignore_index=True)

    return df

# print(cryptocontrol("ethereum"))