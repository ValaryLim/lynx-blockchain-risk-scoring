# imports
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import torch
import transformers as ppb # pytorch transformers

import gzip
import gensim
from gensim import models

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# download at: https://github.com/mmihaltz/word2vec-GoogleNews-vectors
model = models.KeyedVectors.load_word2vec_format(
    'models/word2vec/GoogleNews-vectors-negative300.bin', binary=True)

# functions

'''word embedding'''
def get_embed_features(text):
    '''
    retrieves word embedding from pd.Series of texts
    '''
    # Tokenize the sentence
    tokenized_2vec=text.apply((lambda x: gensim.utils.simple_preprocess(x)))

    # Filter out words not in trained corpus, and add a '0' if sentence is empty
    def filter_vocab(lst):
        if len(lst):
            result = [i for i in lst if i in model.vocab] 
            if not(result):
                result = ['0']
        else: # return non-word
            result = ['0']
        return result

    tokenized_2vec=tokenized_2vec.apply(lambda x: filter_vocab(x))
    embedding=tokenized_2vec.apply(lambda x: model[x])
    #Word2vec performance
    # Taking the average of the vectors of embedding to represent the sentence, alternative is to sum
    features_2vec=np.array(list(embedding.apply(lambda x: sum(x)/len(x))))   
    return features_2vec

def get_embed_features_list(text):
    '''
    retrieves word embedding from list of texts
    '''
    text = list(text)

    # Filter out words not in trained corpus, and add a '0' if sentence is empty
    def filter_vocab(lst):
        if len(lst):
            result = [i for i in lst if i in model.vocab] 
            if not(result):
                result = ['0']
        else: # return non-word
            result = ['0']
        return result

    tokenized_2vec = [gensim.utils.simple_preprocess(x) for x in text]
    filtered_2vec = [filter_vocab(x) for x in tokenized_2vec]
    embedding = [model[x] for x in filtered_2vec]
    features_2vec = [sum(x)/len(x) for x in embedding]

    return features_2vec

def get_results(model, test_features, test_label):
    test_pred = model.predict(test_features)
    print(classification_report(test_label, test_pred, digits=5))
    return None



# training
# all_train = pd.read_csv('data/all_train.csv', index_col = 0)
# train_features = get_embed_features(all_train['text'])

# '''logistic regression'''
# lr = LogisticRegression()
# lr.fit(train_features, all_train['label'])

# '''svm'''
# svm = SVC(probability=True)
# svm.fit(train_features, all_train['label'])

# '''random forest'''
# rf = RandomForestClassifier()
# rf.fit(train_features, all_train['label'])

# testing 
'''
using news as an example, just change the data input accordingly for reddit, twitter and all
'''
# news = pd.read_csv('../data/news_test.csv', index_col = 0)
# news_features = get_embed_features(news['text'])
# get_results(lr, news_features, news['label'])    #logistic regression
# get_results(svm, news_features, news['label'])   #svm 
# get_results(rf, news_features, news['label'])    #random forest

# import pickle
# pickle.dump(svm, open("models/word2vec/svm.txt", 'wb'))
# pickle.dump(lr, open("models/word2vec/lr.sav", 'wb'))
# pickle.dump(rf, open("models/word2vec/rf.sav", 'wb'))
