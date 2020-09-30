import pandas as pd
import numpy as np
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.metrics import roc_curve, recall_score, precision_score, f1_score

SIA = SentimentIntensityAnalyzer()

new_words = {
    'vulnerable':-4.0, 
    'vulnerability':-4.0, 
    'vulnerabilities':-4.0,
    'hack': -4.0,
    'hacked': -4.0,
    'hacker': -4.0,
    'breach': -4.0,
    'breached': -4.0,
    'unsecure': -4.0,
    'compromised': -4.0,
    'steal': -4.0, 
    'stole': -4.0,
    'stolen': -4.0,
    'theft': -4.0, 
    'fraud': -4.0, 
    'fraudster':-4.0,
    'fradulant': - 3.5,
    'scam': -4.0,
    'scammed': -4.0,
    'scammer': -3.0,
    'heist': -4.0, 
    'attack': -4.0, 
    'attacked': -4.0,
    'malware': -4.0, 
    'cryptojacking':-4.0,
    'launder': -4.0, 
    'laundered': -4.0,
    'laundering': -4.0, 
    'allegation': -3.0,
    'allegations':-3.0,
    'allege':-3.0,
    'alleged':-3.0,
    'suspicious': -2.0, 
    'raid': -2.0,
    'emergency': -2.0, 
    'suspect': -2.0, 
    'risk': -3.5, 
    'chaos': -2.0, 
    'shutdown': -3.0, 
    'disable': -2.0, 
    'regulate': 0,
    'phish': -3.0, 
    'phishing':-3.0,
    'illegal': -3.0,
    'fake': -3.0, 
    'suspend':-2.0,
    'leak':-3.0, 
    'leaked':-3.0,
    'exploit': -3.5,
    'exploited':-3.5,
    'malicious': -3.0,
    'threat': -3.0,
    'ponzi': -4.0,
    'freeze': -2.0,
    
    
    'secure': 4.0, 
    'security':4.0,
    'ignorance': 0,
    'compensate': 3.5,
    'compensation':3.5,
    'compaensates':3.5,
    'recover': 4.0,
    'recovered':4.0,
    'recovers':4.0,
    'fud': 3.0,
    'crash':3.0,
    'update':4.0,
    'updates':4.0,
    'profit':3.0,
    'dump':3.0,
    'resolve':3.0,
    'resolution':3.0,
    'deposits':3.0,
    'deposit':3.0,
    'enterprise': 3.0,
    'enterprises':3.0,
    'voting':3.0,
    'opinion':3.0,
    'government':3.0,
    'earned':3.0,
    'earn':3.0,
    'earns':3.0,
    'financial':3.0,
    'drive': 4.0,
    'driving':4.0, 
    'impact':3.0,
    'impacts':3.0,
    'impacted':3.0,
}

#To add new words into the lexicon-based model 
SIA.lexicon.update(new_words)


def vader_predict(text):
    #Threshold found from training
    threshold = 0.81245

    # Get Vader score (score has been corrected s.t. it is in range (0,1))
    # Score of 1 represents high risk

    vader_score = 1-(SIA.polarity_scores(text)['compound'] + 1)/2
    predicted = 0 if vader_score < threshold else 1

    return predicted


