import re
import pandas as pd

def is_alphanumeric(text):
    return any(char.isdigit() for char in text) and any(char.isalpha() for char in text)

def get_coins(text):
    coin_lst = pd.read_csv(r'../scraping/utils/data/coin_lst.csv')['coins'].str.lower().tolist()
    #coin_lst = pd.read_csv(r'./data/coin_lst.csv')['coins'].str.lower().tolist()
    coins = []

    text_words = str(text).lower().split()
    updated_words = []
    
    for word in text_words:
        if (word != "2fa") and is_alphanumeric(word) and (word[0].isdigit() or word[-1].isdigit()): # first or last is digit
            new_word = re.findall('\d+|\D+', word)
            updated_words.extend(new_word)
        else:
            updated_words.append(word)
    text_words = updated_words


    for coin in coin_lst:
        if coin in text_words:
            coins.append(coin)
    return coins

