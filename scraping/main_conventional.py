import pandas as pd
from datetime import datetime, timedelta

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

def retrieve_cases(file, time_frame=7):
    hacks_list = pd.read_csv(file, header=0)
    hacks_list = hacks_list.dropna(how="all")
    hacks_list = hacks_list.fillna('')

    for index, hack in hacks_list.iterrows():
        start_date =  datetime.strptime(hack["start_date"], '%Y-%m-%d')
        end_date = start_date + timedelta(days=time_frame)
        entity1 = hack["exchange"]
        entity2 = hack["coin"]

        if entity1 and entity2: 
            temp_df = conventional_scrape([entity1, entity2], start_date, end_date)
        elif entity1: 
            temp_df = conventional_scrape_by_entity(entity1, start_date, end_date)
        else: 
            temp_df = conventional_scrape_by_entity(entity2, start_date, end_date)
        
        if index == 0: 
            result_df = temp_df
        else: 
            result_df = pd.concat([result_df, temp_df])
    
    # remove duplicates of title, excerpt
    result_df.drop_duplicates(subset =["title", "excerpt"], keep = False, inplace = True) 

    return result_df
    
df = retrieve_cases("data/hacks_list.csv", time_frame=7)
df.to_csv("data/conventional_positive_unfiltered.csv")