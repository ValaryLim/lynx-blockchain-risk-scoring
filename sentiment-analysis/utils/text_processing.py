import pandas as pd
import string
import nltk
from nltk.stem import WordNetLemmatizer # word lemmatizer
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords # stopwords

def text_processing(text, lower=True, remove_punctuation=True, \
    remove_stopwords=True, remove_entity=True, lemmatize=True, stem=False):
    '''
    Accepts a text and processes text
    '''
    # strip non-ascii characters
    text = text.encode('ascii', errors='ignore')
    text = str(text.decode("utf-8"))

    # covert to lowercase
    if lower:
        text = text.lower()

    # remove unnecessary new lines and whitespaces
    text = text.replace("\n", "") 
    text = ' '.join(text.split())

    # remove punctuation
    if remove_punctuation:
        text = text.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))

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
    
    # remove entity name from text
    entity_list = set(pd.read_csv("../data/entity_list.csv", header=0)["entity"])
    entity_list = set(x.lower() for x in entity_list) # convert to lowercase
    if remove_entity:
        text_words = [x for x in text_words if not x.lower() in entity_list]

    return ' '.join(text_words)