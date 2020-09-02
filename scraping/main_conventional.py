import pandas as pd
from datetime import datetime
from theguardian import theguardian_scrape
from cryptocontrol import cryptocontrol_scrape
# from google import google_scrape


def conventional_scrape_by_entity(entity, start_date, end_date):
    column_names = ["date_time", "title", "excerpt", "domain", \
        "article_url", "image_url", "hotness", "activity_hotness"]
    combined_df = pd.DataFrame(columns = column_names)

    # retrieve data
    # theguardian: ["date_time", "title", "excerpt", "article_url"]
    # cryptocontrol: ["date_time", "title", "excerpt", "domain", "article_url", "image_url", "hotness", "activity_hotness"]
    theguardian_df = theguardian_scrape(entity, start_date, end_date)
    cryptocontrol_df = cryptocontrol_scrape(entity)

    # filter cryptocontrol_df based on data that is within start and end date
    mask = (cryptocontrol_df['date_time'] >= start_date) & (cryptocontrol_df['date_time'] <= end_date)
    cryptocontrol_df = cryptocontrol_df[mask]

    # combine the dataframes
    combined_df = cryptocontrol_df.copy(deep=True)
    print(len(combined_df), len(theguardian_df))
    combined_df = combined_df.merge(theguardian_df, how="outer")
    print(len(combined_df))
    print(combined_df)
    
    return 

def conventional_scrape(entity_list, start_date, end_date):
    return 

entity = "ethereum"
start_date = datetime(2019, 9, 1, 0, 0, 0)
end_date = datetime(2020, 9, 2, 23, 59, 59)

conventional_scrape_by_entity(entity=entity, start_date=start_date, end_date=end_date)