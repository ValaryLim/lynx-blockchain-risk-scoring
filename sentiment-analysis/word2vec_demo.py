from gensim import models
import pickle
import gensim
import numpy as np

model = models.KeyedVectors.load_word2vec_format(
    './models/word2vec/GoogleNews-vectors-negative300.bin', binary=True)

svm = pickle.load(open('./models/word2vec/svm.txt', 'rb'))

def get_embed_features(text):
    # Tokenize the sentence
    tokenized_2vec=gensim.utils.simple_preprocess(text)

    # Filter out words not in trained corpus, and add a '0' if setence is empty
    def filter_vocab(lst):
        if len(lst):
            result = [i for i in lst if i in model.vocab] 
            if not(result):
                result = ['0']
        return result

    tokenized_2vec=filter_vocab(tokenized_2vec)
    embedding=model[tokenized_2vec]

    #Taking the average of the vectors of embedding to represent the sentence,      alternative is to sum
    features_2vec=np.array(list(sum(embedding)/len(embedding)))   
    return features_2vec

def word2vec_predict(text):
    features = get_embed_features(text)
    return svm.predict([features])[0]


