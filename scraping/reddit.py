import pandas as pd
from psaw import PushshiftAPI
from datetime import datetime, timedelta

from utils.data_filter import filter_in, filter_out, filter_entity, process_duplicates
from utils.get_coins import get_coins

def reddit_scrape_by_entity(entity, start_date, end_date):
    '''
    Retrieves posts relating to entity from reddit within the stipulated time frame 

    Input:
        entity(string): entity name to retrieve data on
        start_date(datetime): date to begin scraping from
        end_date(datetime): date to stop scraping
    Output:
        df(dataframe): dataframe with columns = [author, url, excerpt, subreddit, title, article_date, type, entity,
                                    	        source_id, content, count, date_time_all, coin, source]
    '''

    # initialise api
    api = PushshiftAPI()

    # convert datetime to timestamp
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())

    # read in list of subreddits
    subreddits = pd.read_csv(r'../scraping/data/subreddit_list.csv')['subreddit'].tolist()
    
    entity = entity.lower()

    ############################## Submissions ################################
    
    # query and generate the related information
    gen_submission = api.search_submissions(q=entity,after= start_epoch, before = end_epoch,
            filter=['created_utc', 'title', 'selftext', 'permalink', 'author', 'subreddit', 'id'],
            subreddit = subreddits)

    # generate dataframe for required data
    df_submission = pd.DataFrame([post.d_ for post in gen_submission])

    # format dataframe 
    if df_submission.empty == False:
        df_submission['title'] = df_submission['title'].apply(lambda x: str(x).lower())
        df_submission['date_time'] = df_submission['created_utc'].apply(lambda x: datetime.fromtimestamp(x))
        df_submission['selftext'] = df_submission['selftext'].apply(lambda x: str(x).lower())
        df_submission['permalink'] = df_submission['permalink'].apply(lambda x: 'www.reddit.com'+ x)
        df_submission['author'] = df_submission['author'].apply(lambda x: x.lower())
        df_submission['subreddit'] = df_submission['subreddit'].apply(lambda x: x.lower())
        df_submission['type'] = 'submission'

        #Remove unecessary columns of data
        df_submission = df_submission.drop(columns = ['created_utc','created'])

        df_submission = df_submission.rename(columns={'selftext': 'excerpt', 'permalink':'article_url'})
    

    ############################## Comments ################################

    # query and generate the related information
    gen_comments = api.search_comments(q=entity,after= start_epoch, before = end_epoch,
            filter=['created_utc', 'body', 'permalink', 'author', 'subreddit', 'id'],
            subreddit = subreddits)


    # generate dataframe for required data
    df_comment = pd.DataFrame([comm.d_ for comm in gen_comments])

    # format dataframe 
    if df_comment.empty == False:
        df_comment['date_time'] = df_comment['created_utc'].apply(lambda x: datetime.fromtimestamp(x))
        df_comment['body'] = df_comment['body'].apply(lambda x: str(x).lower())
        df_comment['permalink'] = df_comment['permalink'].apply(lambda x: 'www.reddit.com'+ x)
        df_comment['author'] = df_comment['author'].apply(lambda x: x.lower())
        df_comment['subreddit'] = df_comment['subreddit'].apply(lambda x: x.lower())
        df_comment['excerpt'] = ''
        df_comment['type'] = 'comments'
        df_comment['id'] = 'comments/' + df_comment['id']

        # remove unecessary columns of data
        df_comment = df_comment.drop(columns = ['created_utc','created'])

        # for comments, there are no titles so the body of the comment will be used as the title
        df_comment = df_comment.rename(columns={'body': 'title', 'permalink':'article_url'})    

    # concatenate submissions and comments dataframe
    df = pd.DataFrame(columns = ['author', 'article_url', 'excerpt', 'subreddit','title', 'date_time','type','entity','id'])
    df = df.append(df_submission)
    df = df.append(df_comment)
    
    df['entity'] = entity
    
    df = df.fillna('')
    df["text"] = df["title"] + " " + df["excerpt"]

    # filter out irrelevant data
    mask1 = list(df.apply(lambda x: filter_out(x["title"]) and filter_out(x["excerpt"]), axis=1))
    df = df[mask1]
    mask2 = list(df.apply(lambda x: filter_in(x["title"]) or filter_in(x["excerpt"]), axis=1))
    df = df[mask2]
    mask3 = list(df.apply(lambda x: filter_entity(str(x["text"]), entity), axis=1))
    df = df[mask3]

    # process duplicates
    df = process_duplicates(df)

    # find all coins that are relevant in text
    df['coin'] = df['text'].apply(lambda x: get_coins(x))

    # reset index
    df = df.reset_index(drop=True)

    # add source column
    df['source'] = 'reddit'

    # rename dataframe using naming convention in final database
    df = df.rename({'text':'content', 'article_url':'url', 'date_time':'article_date','id':'source_id'}, axis = 1)
    
    # keep only relevant columns
    df = df[['source','source_id','article_date','content', 'url','count','entity', 'author','coin']]

    return df


def reddit_scrape(entity_list, start, end):
    '''
    Retrieves posts relating to entitities in entity list from reddit within the stipulated time frame 

    Input:
        entity_list(list): list of entity names to retrieve data on
        start_date(datetime): date to begin scraping from
        end_date(datetime): date to stop scraping
    Output:
        df(dataframe): dataframe with columns = [author, url, excerpt, subreddit, title, article_date, type, entity,
                                    	        source_id, content, count, date_time_all, coin, source]
    '''

    #Create empty dataframe
    output_df = pd.DataFrame()

    #Iterate through list of entities
    for entity in entity_list:

        #retrieve dataframe consisting of all data for each entity
        df = reddit_scrape_by_entity(entity, start, end)

        #Join the dataframes by column
        output_df = output_df.append(df)

    # reset index
    output_df = output_df.reset_index(drop=True)
    
    return output_df

# ################### Testing ###################
# entity = ['okex', 'huobi']
# start_date = datetime(2020, 10, 15)
# end_date = datetime(2020, 10, 26, 23, 59, 59)
# df = reddit_scrape(entity, start_date, end_date)
# df.to_csv(r'~/Desktop/reddit_sample.csv', index = False)
