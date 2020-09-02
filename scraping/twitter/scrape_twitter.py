from twitterscraper import query_tweets
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

cryptoRegExps = {
    "btc": "[13][a-km-zA-HJ-NP-Z1-9]{25,34}$",
    "btc1": "\bbc(0([ac-hj-np-z02-9]{39}|[ac-hj-np-z02-9]{59})|1[ac-hj-np-z02-9]{8,87})\b$",
    "eth": "0x[a-fA-F0-9]{40}$",
    "btc2": "(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$",
    "nem": "[N][A-km-zA-HJ-NP-Z1-9]{26,39}$",
    "ltc": "[LM3][a-km-zA-HJ-NP-Z1-9]{26,33}$",
    "doge": "D{1}[5-9A-HJ-NP-U]{1}[1-9A-HJ-NP-Za-km-z]{32}$",
    "dash": "X[1-9A-HJ-NP-Za-km-z]{33}$",
    "xmr": "4[0-9AB][1-9A-HJ-NP-Za-km-z]{93}$",
    "neo": "A[0-9a-zA-Z]{33}$",
    "xrp": "r[0-9a-zA-Z]{33}$",
}

usefulwebsites = [
    "coinfirm.com",
    "medium.com",
    "coindesk.com",
    "ccn.com",
    "reddit.com",
    "cryptoslate.com",
    "elementus.io",
    "binance.zendesk.com",
    "upbit.com",
]

usefulwords = ["hacked", "hack", "hacker"]


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


def scrape_tweets(
    start_date: datetime, end_date: datetime, exchanges: List[str]
) -> None:
    """
    Scrapes tweets from start_date to end_date using twitterscraper

    Parameters:
    start_date: The date to start scraping
    end_date: The date to stop scraping
    exchanges: list of exchange names to use in query

    Returns:
    None but a csv file with scraped tweets will be created
    """
    import billiard
    exchanges.append("exchange")
    list_of_tweets = []
    print("new version without the 'hack' keyword")

    for ex in exchanges:
        query = f"{ex} since:{start_date:%Y-%m-%d} until:{end_date:%Y-%m-%d}"
        new_tweets = query_tweets(
            f"{ex}",
            begindate=start_date.date(),
            enddate=end_date.date(),
            poolsize=1,
        )
        new_tweets_list = [
            [
                tweet.screen_name,
                tweet.username,
                tweet.user_id,
                tweet.tweet_id,
                tweet.tweet_url,
                tweet.timestamp,
                tweet.timestamp_epochs,
                tweet.text,
                tweet.links,
                tweet.hashtags,
                query,
            ]
            for tweet in new_tweets
        ]
        list_of_tweets.extend(new_tweets_list)

    # Save the retrieved tweets to file:
    file_name = f"{start_date:%Y-%m-%d}_{end_date:%Y-%m-%d}_scrapedtweets.csv"
    with open(file_name, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";", quotechar='"')
        writer.writerows(list_of_tweets)  # Note writerows instead of writerow


def clean_tweets(file_csv: str) -> pd.DataFrame:
    """
    Reads scrapedtweetscsv into a dataframe and cleans it by dropping duplicates,
    rows that contain the column names, rows where the text column is empty

    Parameters:
    file_csv: The name of the scrapedtweetscsv

    Returns:
    A dataframe containing the clean tweets.
    """
    scraped = pd.read_csv(
        file_csv,
        sep=";",
        quotechar='"',
        names=[
            "screen_name",
            "username",
            "user_id",
            "tweet_id",
            "tweet_url",
            "timestamp",
            "timestamp_epochs",
            "text",
            "links",
            "hashtags",
            "searchterm",
        ],
        dtype={"username": str, "tweet_id": str},
        index_col=False,
    )
    scraped["tweet_id"] = (
        scraped["tweet_id"]
        .apply(lambda tweet_id: re.sub(r"[a-zA-Z]", "0", tweet_id))
        .apply(pd.to_numeric)
    )
    scraped = scraped[scraped.username != "username"]
    scraped = scraped.drop_duplicates(subset="tweet_id")
    # some rows in text column is na
    scraped = scraped.dropna(subset=["text"], axis=0)
    return scraped


def unshorten_url(urls: List[str]) -> List[str]:
    """
    Expands urls that were shortened.

    Parameters:
    urls: List of urls in the "links" column

    Returns:
    A list of expanded urls
    """

    def unshorten(url: str) -> str:
        """helper function"""
        try:
            a = requests.head(url, allow_redirects=True).url
            return a
        except:
            return url

    return [unshorten(url) for url in urls]


def check_websites(cell: List[str]) -> List[str]:
    """
    Filters out websites that are not useful.

    Parameters:
    cell: a list of expanded links from the "all_expanded_links" column

    Returns:
    A list of useful websites
    """

    def websites(
        link: str,
        usefulwebsites: List[str] = usefulwebsites,
        usefulwords: List[str] = usefulwords,
    ) -> bool:
        """helper function"""
        link = link.lower()
        is_useful_website = any(word in link for word in usefulwebsites)
        if is_useful_website:
            top_exchange_or_hacked = any(
                word in link for word in top_exchange()
            ) or any(word in link for word in usefulwords)
        return is_useful_website and top_exchange_or_hacked

    return [newcell for newcell in cell if (websites(newcell))]


def filter_words(
    text: str, words: List[str] = ["dark web", "win", "resume", "resuming", "post hack"]
) -> bool:
    """
    Filters out tweets containing words: dark web, win, resuming, resume, post hack

    Parameters:
    text: text of a tweet from the "text" column

    Returns:
    True if the text does not contain the words specified
    """
    return not any(word in text.lower() for word in words)


def filter_wallet_addresses(cell: List[str]) -> List[str]:
    """
    Checks if tweets contain wallet addresses using a regex

    Parameters:
    cell: a row of from "all_text_broken" column

    Returns:
    A list containing wallet addresses matched.
    """

    def match_any_regexp(word, regexps, cryptoRegExps=cryptoRegExps):
        return any(reg_exp.match(word) != None for reg_exp in regexps)

    compiled_regexps = [re.compile(reg_exp) for reg_exp in cryptoRegExps.values()]
    return [word for word in cell if match_any_regexp(word, compiled_regexps)]


def tokenize(text: str) -> str:
    """
    Breaks up tweets (including urls) into a list of words.

    Parameters:
    text: tweet text

    Returns:
    A list of words.
    """
    text = text.lower()
    token = re.compile(r"/|=|\s").split(text)
    return token


def is_wallet_or_website(row: pd.DataFrame) -> bool:
    """
    Selects rows that have either a regex match or website match.

    Parameters:
    row: a row of from the dataframe

    Returns:
    A boolean value indicating whether that row has a wallet address or website match.
    """
    return len(row["address"]) != 0 or len(row["website_match"]) != 0


def filtering(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter the scraped tweets dataframe.

    Parameters:
    df: a dataframe to be filtered

    Returns:
    A filtered dataframe.
    """
    df["links"] = df["links"].apply(ast.literal_eval)  # change a string list to a list
    df["all_expanded_links"] = df["links"].apply(unshorten_url)  # unshorten url
    # drop rows where tweet contain prohibited words
    df = df[df["text"].apply(filter_words)]
    # filter out a specific user (Sumo_Scam), userid used as it is unique and does not change with username
    df = df[df.user_id != 1007703474858070017]
    df["website_match"] = df["all_expanded_links"].apply(
        check_websites
    )  # check if tweet contains relevant websites
    df["all_text_broken"] = df["text"].apply(tokenize)
    df["address"] = df["all_text_broken"].apply(
        filter_wallet_addresses
    )  # check if tweet contains wallet address
    # get the rows that have either a website or regex match
    df = df[df.apply(lambda row: is_wallet_or_website(row), axis=1)]
    return df


def coin_name(addr: List[str]) -> Optional[str]:
    """
    Identify the type of coin of the wallet address present in the tweet.

    Parameters:
    addr: a list of addresses

    Returns:
    A string if the inital list was not empty and the cryptocurrency name exists, else an empty string.
    """
    if len(addr) > 0:
        # Assumes all addresses in a tweet are from the same coin
        addr = addr[0]
        for coin, regs in cryptoRegExps.items():
            regex = re.compile(regs)
            if regex.match(addr) != None:
                return coin
        return ""


def get_exchange(textlist: List[str], exchange: List[str]) -> str:
    """
    Identify the name of the exchange present i      the tweet.

    Parameters:
    textList: a list of words
    exchange: the list of top 200 exchanges

    Returns:
    The name of the exchange mentioned in the tweet if it exists, else an empty string.
    """
    ex = list(filter(lambda word: word.lower() in exchange, textlist))
    if len(ex) > 0:
        return ex[0]


def country_name(text: str) -> Optional[str]:
    """
    Identify the country name present in the tweet.

    Parameters:
    text: text of the tweet

    Returns:
    The name of the country mentioned in the tweet, else return None.
    """
    for country in pycountry.countries:
        if country.name.lower() in text.lower():
            return country.name


def add_new_columns(df: pd.DataFrame, exchanges: List[str]) -> None:
    """Add new columns coin_name, exchange and country into the filtered dataframe.

    Parameters:
    df: dataframe to add new columns to
    exchanges: list of the top 200 exchanges

    Returns:
    None
    """
    df["coin_name"] = df["address"].apply(coin_name)
    df["exchange"] = df["all_text_broken"].apply(
        lambda text: get_exchange(text, exchanges)
    )
    df["country"] = df["text"].apply(country_name)


def run(start_date: datetime, end_date: datetime) -> None:
    """Main function to execute"""
    top_ex = top_exchange()
    scrape_tweets(start_date, end_date, top_ex)
    scrapedtweets = clean_tweets(
        f"{start_date:%Y-%m-%d}_{end_date:%Y-%m-%d}_scrapedtweets.csv"
    )
    filtered = filtering(scrapedtweets)
    # adding new columns
    add_new_columns(filtered, top_ex)
    filtered.to_csv(
        f"{start_date:%Y-%m-%d}_{end_date:%Y-%m-%d}_matchedtweets.csv",
        columns=[
            "screen_name",
            "username",
            "user_id",
            "tweet_id",
            "tweet_url",
            "timestamp",
            "text",
            "hashtags",
            "search_term",
            "all_expanded_links",
            "website_match",
            "address",
            "coin_name",
            "exchange",
            "country",
        ],
        index=False,
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "start_date",
        help="date to start scraping in YYYY-MM-DD format",
        type=lambda d: datetime.strptime(d, "%Y-%m-%d"),
    )
    parser.add_argument(
        "end_date",
        help="date to scrape until in YYYY-MM-DD format (inclusive)",
        type=lambda d: datetime.strptime(d, "%Y-%m-%d"),
    )
    args = parser.parse_args()
    run(args.start_date, args.end_date)
