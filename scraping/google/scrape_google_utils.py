from datetime import date, datetime
from dateutil.parser import parse
import requests
import argparse
from bs4 import BeautifulSoup
from typing import List, Optional
import json
import pandas as pd
import ast
import re
import pycountry
import csv
import os
import sys
import warnings

warnings.filterwarnings("ignore")




def top_exchange():
    """
    Scrapes the names of the top exchanges by trade volume.
    """
    res = requests.get("https://coin.market/exchanges")
    soup = BeautifulSoup(res.text, "html.parser")
    return [
        ele.find("span").text.lower()
        for ele in soup.findAll("div", {"class": "name_td"})
    ]

def scrap_headlines(entity:str, start_date: str, end_date: str):
    
    '''
    Scrap (using GoogleNews API) the top 10 headlines of google news on a particular entity, for a given time range
    Output : Pandas Dataframe with title, short summary, date & url column
    '''
    
    start_date_input=datetime.strptime(start_date, "%Y-%m-%d").strftime("%m-%d-%Y")
    end_date_input=datetime.strptime(end_date, "%Y-%m-%d").strftime("%m-%d-%Y")
    news = GoogleNews(start=start_date_input,end=end_date_input, lang='en', encode='utf-8')
    news.search(f"{entity} crypto")   # Main bulk of time, taking ~2 seconds to search
    
    if pd.DataFrame(news.result()).empty:
        # No relevant articles 
        return pd.DataFrame()
    
    df = pd.DataFrame(news.result())[['title', 'desc', 'date', 'link']]
    
    # Exist date input as '1 month ago' for recent articles
    # df['date'] = pd.to_datetime(df['date'])
    
    # Only get headlines which mention the entity of interest
    df=df[df['title'].str.contains(entity,flags=re.IGNORECASE)].reset_index(drop=True)
    df['entity'] = entity
    
    return df



