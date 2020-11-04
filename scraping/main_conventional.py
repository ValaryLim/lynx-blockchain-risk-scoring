import pandas as pd
from datetime import datetime, timedelta

from theguardian import theguardian_scrape
from google1 import google_scrape
from cryptocontrol import cryptocontrol_scrape

from utils.data_filter import filter_out, filter_entity, process_duplicates
from utils.get_coins import get_coins

def conventional_scrape_by_entity(entity, start_date, end_date):
    '''
    Retrieves articles relating to entity from conventional news sources within stipulated time frame 

    Input:
        entity(string): entity name to retrieve data on
        start_date(datetime): date to begin scraping from
        end_date(datetime): date to stop scraping
    Output:
        df(dataframe): dataframe with columns = [article_date, title, excerpt, source, url, source_id, content,
                                            	entity, count, coin, date_time_all]
    
    '''
    entity = entity.lower()

    column_names = ["date_time", "title", "excerpt", "domain", "article_url",\
        "image_url", "hotness", "activity_hotness"]

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
    
    # get text column
    combined_df["text"] = combined_df["title"].fillna("") + " " + combined_df["excerpt"].fillna("")
    
    # filter out irrelevant data
    mask1 = list(combined_df.apply(lambda x: filter_out(x["title"]) and filter_out(x["excerpt"]), axis=1))
    combined_df = combined_df[mask1]
    mask2 = list(combined_df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    combined_df = combined_df[mask2]

    # label entity and group duplicates
    combined_df["entity"] = entity
    combined_df = process_duplicates(combined_df)

    # get coins that are relevant in text 
    combined_df['coin'] = combined_df['text'].apply(lambda x: get_coins(x))

    # reset index
    combined_df = combined_df.reset_index(drop=True)

    # rename dataframe using naming convention in final database
    combined_df = combined_df.rename({'text':'content', 'article_url':'url', 'domain':'source', \
                                    'date_time':'article_date'}, axis = 1)

    # keep only relevant columns
    combined_df = combined_df[['source','source_id','article_date','content', 'url','count','entity','coin']]

    return combined_df


def conventional_scrape(entity_list, start_date, end_date):
    '''
    Retrieves articles relating to entitities in entity list from conventional news sources within
    the stipulated time frame 

    Input:
        entity_list(list): list of entity names to retrieve data on
        start_date(datetime): date to begin scraping from
        end_date(datetime): date to stop scraping
    Output:
        df(dataframe): dataframe with columns = [article_date, title, excerpt, source, url, source_id, content,
                                            	entity, count, coin, date_time_all]
    '''

    result_df = pd.DataFrame()
    for i in range(len(entity_list)):
        temp_df = conventional_scrape_by_entity(entity=entity_list[i], start_date=start_date, end_date=end_date)
        if i == 0:
            result_df = temp_df
        else:
            result_df = pd.concat([result_df, temp_df], axis=0)
    
    # drop columns where all rows are nan
    result_df = result_df.dropna(axis=1, how='all')

    # reset index
    result_df = result_df.reset_index(drop = True)

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
    result_df.drop_duplicates(subset =["title", "excerpt", "entity"], keep = False, inplace = True) 

    return result_df

def combine_samples(positive=[], negative=[]):
    # read and combine negative datasets first
    for i in range(len(negative)):
        if i == 0:
            result_df = pd.read_csv(negative[0], header=0)
        else:
            temp_df = pd.read_csv(negative[i], header=0)
            result_df = pd.concat([result_df, temp_df])
            
    # read and combine positive datasets
    for i in range(len(positive)):
        if (len(negative) == 0 and i == 0):
            result_df = pd.read_csv(positive[0], header=0)
        else:
            temp_df = pd.read_csv(positive[i], header=0)
            result_df = pd.concat([result_df, temp_df])
    
    # remove duplicates in results
    result_df.drop_duplicates(subset=["title", "excerpt", "entity"], keep="last")

    # additional cleaning
    result_df = result_df.dropna(how="all")
    result_df = result_df.fillna('')

    return result_df


# entity = "upbit"
# start_date = datetime(2019, 12, 1, 0, 0, 0)
# end_date = datetime(2019, 12, 31, 23, 59, 59)
# print(conventional_scrape_by_entity(entity, start_date, end_date))

#### UNCOMMENT TO RETRIEVE POSITIVE TEST CASES ####
# df = retrieve_cases("data/hacks_list.csv", time_frame=7)
# df.to_csv("data/conventional_positive_unfiltered.csv")
###################################################

#### UNCOMMENT TO RETRIEVE NEGATIVE TEST CASES ####
# start_date = datetime(2020, 1, 1, 0, 0, 0)
# end_date = datetime(2020, 10, 30, 23, 59, 59)
# entity_list = list(pd.read_csv("data/entity_list.csv", header=0)["entity"])
# df = conventional_scrape(entity_list, start_date, end_date)
# df.to_csv("data/2020_conventional.csv")
###################################################

#### UNCOMMENT TO COMBINE SAMPLES ####
# df = combine_samples(positive=["data/conventional_positive.csv"], negative=["data/conventional_negative_unfiltered.csv"])
# df.to_csv("data/conventional_sample.csv")
######################################
