import pandas as pd 
import numpy as np
from sklearn.metrics import roc_curve, recall_score, precision_score, f1_score

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer

#Import training data
train = pd.read_csv('./data/all_train.csv')

#Import test data
test_all = pd.read_csv('./data/all_test.csv')
test_news = pd.read_csv('./data/news_test.csv')
test_reddit = pd.read_csv('./data/reddit_test.csv')
test_twitter = pd.read_csv('./data/twitter_test.csv')

#Initialise VADER sentiment analyzer
SIA = SentimentIntensityAnalyzer()

#Get threshold to best split the data from the train data
def get_threshold(df):
    
    #Get polarity score and scale it to be in range(0,1)
    df['vader'] = df.text.apply(lambda x: 1-(SIA.polarity_scores(x)['compound'] + 1)/2)
    
    #Get threshold to best split the data from the train data
    fpr, tpr, thresholds = roc_curve(df['label'], df['vader'], pos_label=1)
    
    results = pd.DataFrame()
    
    results['fpr'] = fpr
    results['tpr'] = tpr
    results['thresholds'] = thresholds
    
    # Maximise tpr and minimise fpr
    results['overall_pr'] = tpr-fpr
    
    threshold = results['thresholds'].iloc[results['overall_pr'].idxmax()]
    
    return threshold


# Predict and get relevant metrics (recall, precision, f1)
def get_metrics(df, threshold):
    
    df['vader'] = df.text.apply(lambda x: 1-(SIA.polarity_scores(x)['compound'] + 1)/2)
    df['predicted'] = df.vader.apply(lambda x: 0 if x < threshold else 1)

    recall = recall_score(df['label'], df['predicted'], pos_label = 1) # TP/(TP + FN)
    prec = precision_score(df['label'], df['predicted'], pos_label = 1)# TP/(TP + FP)
    f1 = f1_score(df['label'], df['predicted'], pos_label = 1)

    print('recall: '+ str(recall))
    print('precision: '+ str(prec))
    print('f1: '+ str(f1))

#Get threshold from train data
threshold = get_threshold(train)

# Test on all dataset
get_metrics(test_all, threshold)

# Test on news dataset
get_metrics(test_news, threshold)

# Test on reddit dataset
get_metrics(test_reddit, threshold)

# Test on twitter dataset
get_metrics(test_twitter, threshold)

######################### REVIEW ##########################
# This section helps to get the data that have been wrongly categorised and this will be passed 
# through an exploratory analysis to get a wordcloud consisting of most frequently used words in the 
# wrong category. These words are then sieved through manually and will be used as keywords to be added in 
# the dictionary with a repective sentiment score in order to build a better dictionary for out context of 
# risk scoring, which is the custom vader model.

from wordcloud import WordCloud
import matplotlib.pyplot as plt

#Get wrongly categorised with the threshold from the training data (return 2 dataframes)
def get_wrong_cat(train, threshold):
    train['vader'] = train.text.apply(lambda x: 1-(SIA.polarity_scores(x)['compound'] + 1)/2)

    train['predicted'] = train.vader.apply(lambda x: 0 if x < threshold else 1)

    train_actual0 = train[(train['predicted'] == 1) & (train['label'] == 0)]
    train_actual1 = train[(train['predicted'] == 0) & (train['label'] == 1)]
    
    return train_actual0, train_actual1

train_actual0, train_actual1 = get_wrong_cat(train, threshold)

def show_wordcloud(data, title = None):
    wordcloud = WordCloud(
        background_color = 'white',
        max_words = 200,
        max_font_size = 40, 
        scale = 3,
        random_state = 42
    ).generate(str(data))

    fig = plt.figure(1, figsize = (10, 10))

    plt.axis('off')

    if title: 
        fig.suptitle(title, fontsize = 20)
        fig.subplots_adjust(top = 2.3)
    plt.imshow(wordcloud)
    plt.show()

# show_wordcloud(train_actual0['text'])
# show_wordcloud(train_actual1['text'])