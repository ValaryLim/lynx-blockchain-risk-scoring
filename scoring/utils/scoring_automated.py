import pandas as pd

def entity_risk_score(df, entity, start_date, end_date, 
                      weights = {"news": 0.5, "reddit": 0.25, "twitter": 0.25}): 
    '''
    Retrieve dataframe of entity information (database 1) and outputs risk score for each day (database 2)
    
    Parameters
    ------------
    df : pd.DataFrame
        Dataframe with information on article source, date, and predicted risk
    
    entity : str
        Name of entity
    
    start_date : datetime.datetime
        First date to include in dataframe (inclusive)
        
    end_date : datetime.datetime
        Last date to include in dataframe (inclusive)
    
    weights : dictionary
        Mapping of source (news, reddit, twitter) to relative weights/contribution to overall score
        Default: {"news": 0.5, "reddit": 0.25, "twitter": 0.25}, i.e. placing larger importance on news
    
    Returns 
    -----------
    risk_score : pd.DataFrame
        Database 2, i.e. combined risk score for each day over time
    '''
    entity = entity.lower()

    # set counter (required for future processing)
    if "count" in df.columns:
        df["counter"] = df["count"]

    # determine entity threshold
    thresholds_df = pd.read_csv('../scoring/utils/data/entity_thresholds.csv')
    thresholds_df = thresholds_df[thresholds_df["entity"] == entity] # filter for entity
    thresholds_df = thresholds_df.reset_index()
    thresholds = dict(thresholds_df) # convert to dict
    thresholds = {"news": thresholds["news"][0], \
        "reddit": thresholds["reddit"][0], \
            "twitter": thresholds["twitter"][0]} # process dict


    # prepare news scores
    news_score = weighted_average_risk(df, 
                                       start_date=start_date, end_date=end_date, 
                                       source="news", threshold=thresholds["news"])
    # prepare reddit scores
    reddit_score = weighted_average_risk(df, 
                                         start_date=start_date, end_date=end_date, 
                                         source="reddit", threshold=thresholds["reddit"])
    # prepare twitter scores
    twitter_score = weighted_average_risk(df, 
                                          start_date=start_date, end_date=end_date, 
                                          source="twitter", threshold=thresholds["twitter"])
    
    # combine dataframes
    overall_score = pd.merge(news_score, reddit_score, on="date", how="outer")
    overall_score = pd.merge(overall_score, twitter_score, on="date", how="outer")
    
    # generate overall score
    overall_score["score"] = weights["news"] * overall_score["news_score"] + \
        weights["reddit"] * overall_score["reddit_score"] + \
        weights["twitter"] * overall_score["twitter_score"]
    
    # sort rows by date
    overall_score = overall_score.sort_values(by="date")

    # add entity column
    overall_score["entity"] = entity
    
    return overall_score


def weighted_average_risk(df, start_date, end_date, source="news", threshold=0):
    '''
    Outputs risk score for each day for specific source
    
    Parameters
    ------------
    df : pd.DataFrame
        Dataframe with information on article source, date, and predicted risk
    
    start_date : datetime.datetime
        First date to include in dataframe (inclusive)
        
    end_date : datetime.datetime
        Last date to include in dataframe (inclusive)
    
    source : str
        "news" / "reddit" / "twitter"
        Filters only articles from specific source (if pass empty string, no filter)
    
    threshold : int
        Minimum number of articles present for risk score to be taken into account
        
    Returns 
    -----------
    risk_score : pd.DataFrame
        Risk score for each day over time for particular source
    '''
    # copy dataframe
    df_copy = df.copy(deep=True)
    
    # compute risk * count of each article
    df_copy["risk_count"] = df_copy["predicted_risk"] * df_copy["counter"]
    
    # filter by source
    if source == "news":
        df_copy = df_copy[df_copy["source"]!="twitter"]
        df_copy = df_copy[df_copy["source"]!="reddit"]
    elif source == "twitter" or source == "reddit": # source is twitter or reddit
        df_copy = df_copy[df_copy["source"]==source]
    
    # get dates of articles
    df_copy['article_date'] = pd.to_datetime(df_copy['article_date'], format='%Y-%m-%d %H:%M:%S')
    df_copy["date"] = df_copy["article_date"].dt.date
    
    # get sum of risk score by date
    risk_score = df_copy.groupby(by=["date"]).risk_count.sum()
    risk_score = pd.DataFrame(risk_score)
    risk_score = risk_score.reset_index()
    risk_score.columns = ["date", "score"]

    # retrieve counts per day
    count = df_copy.groupby(by=["date"]).counter.sum()
    count = pd.DataFrame(count)
    count = count.reset_index()
    count.columns = ["date", "count"]
    
    # combine df
    risk_score = pd.merge(risk_score, count, on="date")
    
    # compute risk
    risk_score["score"] = risk_score["score"] / risk_score["count"]

    # filter 
    risk_score = filter_risk(risk_score, threshold=threshold)
    
    # get sum of risk score
    risk_score["score"] = risk_score["score"] / risk_score["count"]
    
    # fill missing dates
    risk_score = risk_score[["date", "score"]]
    risk_score = reindex_dataframe(risk_score, start_date, end_date)
    
    # rename columns
    risk_score.columns = ["date", source + "_score"]
    
    # fill empty values
    risk_score = risk_score.fillna(0)
    
    return risk_score

def reindex_dataframe(df, start_date, end_date):
    '''
    Fill missing dates with 0 risk value
    
    Parameters
    ------------
    df : pd.DataFrame
        Dataframe with the dates and risk score associated with each date
    
    start_date : datetime.datetime
        First date to include in dataframe (inclusive)
        
    end_date : datetime.datetime
        Last date to include in dataframe (inclusive)
    
    Returns 
    ------------
    updated_df : pd.DataFrame
        Updated dataframe with missing dates filled as 0 risk score
    '''
    # create copy of dataframe
    updated_df = df.copy(deep=True)
    
    # generate new index from date range
    date_idx = pd.date_range(start_date, end_date, freq="D")
    
    # change index
    updated_df = updated_df.set_index("date")
    
    # reindex
    updated_df = updated_df.reindex(date_idx)
    
    # reset index
    updated_df = updated_df.reset_index()
    updated_df.columns = ["date", "score"]
    
    return updated_df

def filter_risk(risk_df, threshold):
    '''
    Parameters
    ------------
    risk_df : pd.DataFrame
        Dataframe including the count of articles/posts per day and predicted risk for the day
    
    threshold : float
        Minimum count of articles/posts per day for risk score to be used
    
    Returns 
    ------------
    updated_df : pd.DataFrame
        Dataframe with updated risk score, where risk score is 0 for days where article count does not meet threshold
    '''
    updated_risk = []
    
    for ind, row in risk_df.iterrows():
        if row["count"] < threshold:
            # count does not meet threshold, replace risk with 0
            updated_risk.append(0)
        else:
            # count meets threshold, do not replace risk
            updated_risk.append(row["score"])
    
    # update risk
    updated_df = risk_df.copy(deep=True)
    updated_df["score"] = updated_risk
    
    return updated_df