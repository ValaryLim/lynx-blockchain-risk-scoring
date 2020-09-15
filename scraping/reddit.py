import pandas as pd
from psaw import PushshiftAPI
from datetime import datetime, timedelta
from utils/data_filter import filter_out, filter_in


def reddit_scrape_byentity(entity, start_date, end_date):

    api = PushshiftAPI()

    #Convert datetime to timestamp
    start_epoch = int(start_date.timestamp())
    end_epoch = int(end_date.timestamp())

    #List of subreddits
    subreddits = ['0xproject', '0xuniverse', 'aave_official', 'abcc', 'airswap', 'bancor', 'batproject',\
        'bgogo','bnbtrader', 'binance', 'bitfinex', 'bitmartexchange', 'bitmax', 'bitstamp',\
        'bitstampofficial','bittrex','bitpanda', 'blockfi', 'celsiusnetwork', 'cobinhood', 'cobo',\
        'coinbase', 'coinex', 'coinmine','compound', 'cossio', 'crypto_com', 'cryptokitties', 'cryptopia',\
        'dapps', 'ddex', 'decentraland', 'ethfinex', 'freewallet', 'gemini', 'genesismining', 'gnosispm',\
        'godsunchained', 'hitbtc', 'hotbit', 'huobiglobal', 'huobi', 'projecthydro', 'idex', 'kraken', 'kucoin',\
        'miningpoolhub', 'nexo', 'okex', 'poloniex', 'quadrigacx', 'shapeshiftio', 'storj', 'switcheo',\
        'synthetix_io', 'tether', 'tradeioico', 'uniswap', 'cryptocurrency', 'cryptocurrencies',\
        'cryptocurrencytrading', 'cryptomarkets', 'crypto_currency_news', 'bitcoin', 'btc', 'icocrypto',\
        'bitcoinmarkets', 'bitcoinbeginners', 'bitcoinmining', 'bitcoinuk', 'ethereum', 'ethereumclassic',\
        'ethtrader', 'ethermining', 'ethereumnoobies', 'ethfinance', 'eth', 'ripple', 'bitcoincash', 'litecoin',\
        'cardano', 'neo', 'iota', 'vertcoin', 'eos', 'bitcoincashsv', 'bitcoinsv', 'litecoinmarkets', 'ethdev',\
        'digibyte','cryptonews']


    ############################## Submissions ################################
    
    #Query and generate the related information
    gen_submission = api.search_submissions(q=entity,after= start_epoch, before = end_epoch,
            filter=['created_utc', 'title', 'selftext', 'permalink', 'author', 'subreddit'],
            subreddit = subreddits)

    #Generate dataframe for required data
    df_submission = pd.DataFrame([post.d_ for post in gen_submission])

    #Format dataframe 
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

    #Query and generate the related information
    gen_comments = api.search_comments(q=entity,after= start_epoch, before = end_epoch,
            filter=['created_utc', 'body', 'permalink', 'author', 'subreddit'],
            subreddit = subreddits)


    #Generate dataframe for required data
    df_comment = pd.DataFrame([comm.d_ for comm in gen_comments])

    #Format dataframe 
    if df_comment.empty == False:
        df_comment['date_time'] = df_comment['created_utc'].apply(lambda x: datetime.fromtimestamp(x))
        df_comment['body'] = df_comment['body'].apply(lambda x: str(x).lower())
        df_comment['permalink'] = df_comment['permalink'].apply(lambda x: 'www.reddit.com'+ x)
        df_comment['author'] = df_comment['author'].apply(lambda x: x.lower())
        df_comment['subreddit'] = df_comment['subreddit'].apply(lambda x: x.lower())
        df_comment['excerpt'] = ''
        df_comment['type'] = 'comments'

        #Remove unecessary columns of data
        df_comment = df_comment.drop(columns = ['created_utc','created'])

        #For comments, there are no titles so the body of the comment will be used as the title
        df_comment = df_comment.rename(columns={'body': 'title', 'permalink':'article_url'})    



    #Concatenate submissions and comments dataframe
    df = df_submission.append(df_comment)
    df['entity'] = entity
    
    #Filter the data with relevant keywords
    df.fillna('')
    df = df[df.apply(lambda x: filter_in(x["title"]) or filter_in(x["excerpt"]), axis=1)]
    df = df[df.apply(lambda x: filter_out(x["title"]) and filter_out(x["excerpt"]), axis=1)]


    #Output dataframe columns: [author, title, article_url, date_time, subreddit, excerpt]
    return df




def reddit_scrape(entity_list, start, end):
    #Create empty dataframe
    output_df = pd.DataFrame()

    #Iterate through list of entities
    for entity in entity_list:

        #retrieve dataframe consisting of all data for each entity
        df = reddit_scrape_byentity(entity, start, end)

        #Join the dataframes by column
        output_df = output_df.append(df)

    return output_df


