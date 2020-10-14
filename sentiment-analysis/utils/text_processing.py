import re
import pandas as pd
import string
import nltk
from nltk.stem import WordNetLemmatizer # word lemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords # stopwords

def is_alphanumeric(text):
    return any(char.isdigit() for char in text) and any(char.isalpha() for char in text)

def is_transaction_hash(text):
    return is_alphanumeric(text) and len(text) > 20

def text_processing(text, 
                    lower=True, 
                    remove_url=True, 
                    remove_punctuation=True, 
                    remove_stopwords=False, 
                    replace_entity=False, 
                    replace_hash=False,
                    split_alphanumeric=False,
                    lemmatize=False,
                    stem=False):
    '''
    Accepts a text and options to run the following processing functions:
    '''
    # strip non-ascii characters
    text = text.encode('ascii', errors='ignore')
    text = str(text.decode("utf-8"))

    # covert to lowercase
    if lower:
        text = text.lower()

    # remove url 
    if remove_url:
        text = re.sub(r'http\S+', '', text)
    
    # remove punctuation
    if remove_punctuation:
        text = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))
        
    # remove unnecessary new lines and whitespaces
    text = text.replace("\n", "") 
    text = ' '.join(text.split())
    
    # tokenize
    text_words = nltk.word_tokenize(text)

    # lemmatize
    if lemmatize:
        wordnet_lemmatizer = WordNetLemmatizer()
        text_words = [wordnet_lemmatizer.lemmatize(x, pos="v") for x in text_words]

    # stem
    if stem:
        stemmer = SnowballStemmer("english")
        text_words = [stemmer.stem(x) for x in text_words]

    # remove stop words
    if remove_stopwords:
        stop = list(stopwords.words('english'))
        keep_stopwords = ["no", "not", "nor"]
        for word in keep_stopwords:
            stop.remove(word)
            stop = set(stop)
        text_words = [x for x in text_words if not x.lower() in stop]
    
    # replace entity
    entity_list = set(pd.read_csv("../data/entity_list.csv", header=0)["entity"])
    entity_list = set(x.lower() for x in entity_list) # convert to lowercase
    if replace_entity:
        text_words = [x if not (x.lower() in entity_list) else "entity" for x in text_words]
        
    # replace transaction hashes
    if replace_hash:
        text_words = [x if not is_transaction_hash(x) else "hash" for x in text_words]
    
    # split alphanumeric numbers
    updated_words = []
    if split_alphanumeric:
        for word in text_words:
            if (word != "2fa") and is_alphanumeric(word) and (word[0].isdigit() or word[-1].isdigit()): # first or last is digit
                new_word = re.findall('\d+|\D+', word)
                updated_words.extend(new_word)
            else:
                updated_words.append(word)
        text_words = updated_words
    
    return ' '.join(text_words)