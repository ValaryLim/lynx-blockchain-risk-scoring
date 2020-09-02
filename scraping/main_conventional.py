import pandas as pd
from datetime import datetime

from google import google_scrape
from theguardian import theguardian_scrape
from cryptocontrol import cryptocontrol_scrape

def conventional_scrape_by_entity(entity, start_date, end_date):
    column_names = ["date_time", "title", "excerpt", "domain", \
        "article_url", "image_url", "hotness", "activity_hotness"]
    combined_df = pd.DataFrame(columns = column_names)

    # retrieve data
    # google: ['date_time', 'title', 'excerpt', 'domain', 'article_url']
    # theguardian: ["date_time", "title", "excerpt", "article_url"]
    # cryptocontrol: ["date_time", "title", "excerpt", "domain", "article_url", "image_url", "hotness", "activity_hotness"]
    google_df = google_scrape(entity, start_date, end_date)
    theguardian_df = theguardian_scrape(entity, start_date, end_date)
    theguardian_df["domain"] = "theguardian"

    cryptocontrol_scraped = False
    try:
        cryptocontrol_df = cryptocontrol_scrape(entity)
        # filter cryptocontrol_df based on data within start and end date
        mask = (cryptocontrol_df['date_time'] >= start_date) & (cryptocontrol_df['date_time'] <= end_date)
        cryptocontrol_df = cryptocontrol_df[mask] 
        cryptocontrol_scraped = True
    except:
        pass

    # combine the dataframes
    if cryptocontrol_scraped:
        combined_df = pd.concat([cryptocontrol_df, google_df, theguardian_df])
    else: 
        combined_df = pd.concat([google_df, theguardian_df])
    
    return combined_df

def conventional_scrape(entity_list, start_date, end_date):
    result_df = pd.DataFrame()
    for i in range(len(entity_list)):
        temp_df = conventional_scrape_by_entity(entity=entity_list[i], start_date=start_date, end_date=end_date)
        temp_df["entity"] = entity_list[i]
        if i == 0:
            result_df = temp_df
        else:
            result_df = result_df.merge(temp_df, how="outer")
    
    # drop columns where all rows are nan
    result_df = result_df.dropna(axis=1, how='all')

    return result_df

# entity = "ethereum"
# start_date = datetime(2019, 8, 1, 0, 0, 0)
# end_date = datetime(2020, 9, 2, 23, 59, 59)
# entity_list = ["binance", "ethereum", "upbit"]
# print(conventional_scrape_by_entity(entity="ethereum", start_date=start_date, end_date=end_date))
# print(conventional_scrape(entity_list=entity_list, start_date=start_date, end_date=end_date))