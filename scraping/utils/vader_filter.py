# used to clean data before labelling them

# import nltk
# nltk.download('vader_lexicon')

import numpy as np
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from data_filter import filter_out

def filter_vader(sentence, threshold=0.5):
    '''
    Output: 0 if low risk, 1 if positive risk
    '''
    score = SentimentIntensityAnalyzer().polarity_scores(sentence)['compound']

    if score > threshold: # positive -> low risk
        return 0
    elif score < - threshold: # negative -> high risk
        return 1
    else: # neutral -> ignore
        return np.nan

def clean_data(input_data, output_data):
    for i in range(len(input_data)):
        # read data
        sample = pd.read_csv(input_data[i], index_col=0)

        # remove duplicates
        sample.drop_duplicates(subset =["title", "excerpt", "entity"], keep = False, inplace = True) 

        # label data
        sample["text"] = sample["title"].fillna('') + " " + sample["excerpt"].fillna('')

        # apply filters
        sample = sample[sample.apply(lambda x: filter_out(x["text"]), axis=1)]
        sample["label"] = sample.text.apply(lambda x: filter_vader(x))
        sample = sample.dropna(subset=["label"])
        
        sample.to_csv(output_data[i], index=False)


# uncomment to retrieve filtered data
# input_data = ['../data/cryptonews_sample.csv', '../data/cryptoslate_sample.csv', \
#     '../data/forbes_sample.csv']
# output_data = ['../data/cryptonews_sample_filtered.csv', '../data/cryptoslate_sample_filtered.csv', \
#     '../data/forbes_sample_filtered.csv']
# clean_data(input_data, output_data)