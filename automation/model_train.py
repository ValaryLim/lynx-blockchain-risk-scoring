import numpy as np
import pandas as pd

from utils.text_processing import text_processing
from simpletransformers.classification import ClassificationModel, ClassificationArgs

def to_binary(prob):
    if prob > 0.5:
        return 1
    return 0

def model_train(data, output_dir='models/'):
    '''
    Trains a roberta model based on input data.
    Inputs: 
      data (pd.DataFrame): with columns content (text), ground_truth_risk (label), probability_risk.
      output_dir (str): output path or directory to save model.
    Output:
      None, model will already be saved in specified output directory.
    '''

    # extract relevant columns
    df = pd.DataFrame(data[['content', 'ground_truth_risk', 'probability_risk']])

    # if ground truth risk is NA, convert probability to ground truth risk to train
    df_NA = df[df['ground_truth_risk'].isnull()]
    df_NA['ground_truth_risk'] = df_NA.apply(lambda x: to_binary(x['probability_risk']), axis=1)

    # update df
    df = df.dropna(subset=['ground_truth_risk'])
    df = pd.concat([df, df_NA], ignore_index=True)

    # format df for training
    df = pd.DataFrame(df[['content', 'ground_truth_risk']])
    # rename columns - requirement of the simpletransformers package
    df = df.rename({'content': 'text', 'ground_truth_risk': 'labels'}, axis=1)


    # processing text column
    df['text'] = df.apply(lambda x: text_processing(x.text,                     
                                                    lower=False, 
                                                    remove_url=True, 
                                                    remove_punctuation=False, 
                                                    remove_stopwords=False, 
                                                    replace_entity=True, 
                                                    replace_hash=True,
                                                    split_alphanumeric=False,
                                                    lemmatize=False,
                                                    stem=False), axis=1)

    # initialise Model
    model_args = ClassificationArgs(num_train_epochs=2, learning_rate = 5e-5, \
                                    output_dir=output_dir)
    model = ClassificationModel(model_type = 'roberta', model_name = 'roberta-base', \
                                args = model_args, use_cuda = False)
    # train the model
    model.train_model(df)

    return
