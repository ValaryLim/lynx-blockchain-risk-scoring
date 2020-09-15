import string # for punctuation
import math
import nltk
from nltk.stem import WordNetLemmatizer 

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