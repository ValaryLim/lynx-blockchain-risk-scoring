import pandas as pd
from psaw import PushshiftAPI
from datetime import datetime

#####Contains 2 functions for retrieval of submission and comments data
#####Functions: reddit_submissions_scrape & reddit_comments_scrape 

#Retrieving submission data from reddit through pushshift
def reddit_submissions_scrape(entity, start_date, end_date):

    api = PushshiftAPI()

    #Convert datetime to timestamp
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())

    #Query and generate the related information
    gen = api.search_submissions(q=entity,after= start_epoch, before = end_epoch,
            filter=['created_utc', 'title', 'selftext', 'permalink', 'author', 'subreddit', 'score'])

    #Generate dataframe for required data
    df = pd.DataFrame([thing.d_ for thing in gen])

    #Format dataframe 
    df['title'] = df['title'].apply(lambda x: str(x).lower())
    df['date_time'] = df['created_utc'].apply(lambda x: datetime.fromtimestamp(x))
    df['selftext'] = df['selftext'].apply(lambda x: str(x).lower())
    df['permalink'] = df['permalink'].apply(lambda x: 'www.reddit.com'+ x)
    df['author'] = df['author'].apply(lambda x: x.lower())
    df['subreddit'] = df['subreddit'].apply(lambda x: x.lower())
    df = df.drop(columns = ['created_utc','created'])
    df = df.rename(columns={'selftext': 'exceprt', 'permalink':'article_url'})

    return df

# ###############Testing###################
# entity = 'binance'
# start_date = datetime(2019, 5, 1)
# end_date = datetime(2019, 6, 1)
# df = reddit_submissions(entity, start_date, end_date)
# #########################################

# df.to_csv(r'file.csv')



#Retrieving comments data from reddit through pushshift
def reddit_comments_scrape(entity, start_date, end_date):

    api = PushshiftAPI()

    #Convert datetime to timestamp
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())


    #Query and generate the related information
    gen = api.search_comments(q=entity,after= start_epoch, before = end_epoch,
            filter=['created_utc', 'body', 'permalink', 'author', 'subreddit', 'score', 'parent_id'])


    #Generate dataframe for required data
    df = pd.DataFrame([thing.d_ for thing in gen])


    #Format dataframe 
    df['date_time'] = df['created_utc'].apply(lambda x: datetime.fromtimestamp(x))
    df['body'] = df['body'].apply(lambda x: str(x).lower())
    df['permalink'] = df['permalink'].apply(lambda x: 'www.reddit.com'+ x)
    df['author'] = df['author'].apply(lambda x: x.lower())
    df['subreddit'] = df['subreddit'].apply(lambda x: x.lower())

    df = df.drop(columns = ['created_utc','created'])

    #For comments, there are no titles so the body of the comment will be used as the title
    df = df.rename(columns={'body': 'title', 'permalink':'article_url'})

    return df


# ###############Testing################
# entity = 'binance'
# start_date = datetime(2019, 5, 1)
# end_date = datetime(2019, 6, 1)
# df = reddit_comments(entity, start_date, end_date)
# ######################################

# df.to_csv(r'file.csv')

