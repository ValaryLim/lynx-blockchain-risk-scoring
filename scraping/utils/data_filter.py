import string # for punctuation
import math
import nltk
from nltk.stem import WordNetLemmatizer 
from langdetect import detect

def filter_entity(sentence, entity):
    entity_list = str(entity).lower().split()
    sentence_list = str(sentence).lower().split()
    found = 0
    for entity_word in entity_list:
        if entity_word in sentence_list:
            found += 1
    return found == len(entity_list)

def filter_out(sentence):
    '''
    Output: True if sentence should be kept, False otherwise 
    '''
    # set of words to filter out (lemmatized)
    filter_set = {'price', 'rat', 'fee', 'liquidity', 'trade', 'trade', 'invest', 'value',\
        'update', 'winner', 'history', 'competition', 'review', 'welcome', 'bull', 'bear', \
        'perform', 'cost', 'discount', 'spend', 'perform', 'potential', 'interest', 'success',\
        'prediction', 'forecast', 'top', 'return', 'gift', 'demand', 'trend', 'shop', 'buy',\
        'brief', 'tip', 'complete', 'expand', 'improve', 'retail', 'explain', 'investment', \
        'sentiment', 'rewind', 'trader', 'trade', 'innovation', 'joke', 'tax', 'pros', 'rewind', \
        'hype', 'how', 'war', 'drop', 'falling', 'inflation', 'remedy', 'recover', 'introduction',\
        'investors', 'dip', 'legalize', 'regulate', 'launch', 'support', 'grant', 'arbitrage'}

    # if there exist no sentence (excerpt), return True
    if type(sentence) != str:
        if math.isnan(sentence):
            return True

    # pre-process sentence
    processed_sentence = pre_processing(sentence)

    for word in processed_sentence:
        if word in filter_set: 
            return False

    return True


def filter_in(sentence):
    '''
    Output: True if sentence should be kept, False otherwise 
    '''
    # set of words to filter out (lemmatized)
    filter_set = {'unsecure','insecure', 'secure', 'security', 'breach', 'hack', 'compromise',\
        'steal', 'fraud', 'scam', 'heist', 'attack', 'malware', 'suspicious', 'cryptojacking',\
        'launder', 'allegation','raid', 'emergency', 'suspect', 'risk', 'chaos', 'assault',\
        'theft', 'criticism','shutdown', 'down', 'disable', 'regulate', 'phish', 'illegal',\
        'fake', 'suspend','vulnerable', 'leak', 'fraudster'}

    # pre-process sentence
    processed_sentence = pre_processing(sentence)

    for word in processed_sentence:
        if word in filter_set: 
            return True
    
    return False

def pre_processing(sentence):
    wordnet_lemmatizer = WordNetLemmatizer()

    # covert to lowercase
    sentence = sentence.lower()

    # remove punctuation
    sentence = sentence.translate(str.maketrans(string.punctuation, ' '*len(string.punctuation)))

    # split sentence
    sentence_words = nltk.word_tokenize(sentence)

    # lemmatize
    lemma_words = [wordnet_lemmatizer.lemmatize(x, pos="v") for x in sentence_words]
    
    return lemma_words

def process_duplicates(df):
    '''
    Accepts a pandas dataframe and outputs 
    '''
    if df.empty:
        df["count"] = 0
        df["date_time_first"] = ""
        return df
    
    # assign count based on text and entity
    df["count"] = df.groupby(by=["text", "entity"]).text.transform('size')

    # get array of all date times
    df = df.merge(df.groupby(['text', 'entity']).date_time.agg(list).reset_index(), 
              on=['text', 'entity'], 
              how='left',
                  suffixes=['', '_all'])
    
    # drop duplicates, keeping the first
    df = df.drop_duplicates(subset=["text", "entity"], keep='first')

    return df

def enTweet(sentence):
    '''
    Checks that tweet is in english
    '''
    try:
        language = detect(sentence)
        if(language == 'en'):
            return True
        else:
            return False
    except:
        print('exception!')
        return False