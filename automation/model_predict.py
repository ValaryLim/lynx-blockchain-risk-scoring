from simpletransformers.classification import ClassificationModel, ClassificationArgs
from scipy.special import softmax

#Import text processor
from utils.text_processing import text_processing

def model_predict(text):
    '''
    Takes in an array of text and returns predicted probability of risk.

    Input:
        text (arr): E.g. data[['content']]
    Output: 
        pred (arr): returns label of 0 for low risk and 1 for high risk based on prob_risk
        prob_risk (arr): E.g. data['probability_risk'] = model_predict(data[['content']])
        pred_risk (arr): Risk score for each article
    '''

    #read text file to get model path
    model_txt = open("../automation/curr_model.txt", "r")
    model_path = model_txt.read()
    model_txt.close()

    # loading saved model, specifying same args as model init
    # model names: path to directory containing model files
        # model naming convention : roberta_YYYY_MM    
    model_args = ClassificationArgs(num_train_epochs=2, learning_rate=5e-5)
    model = ClassificationModel(model_type = 'roberta', model_name = model_path, \
                                args = model_args, use_cuda = False)

    # Preprocess text
    processed_text = text.apply(lambda x: text_processing(x, lower=False, 
                                    remove_url=True, 
                                    remove_punctuation=False, 
                                    remove_stopwords=False, 
                                    replace_entity=True, 
                                    replace_hash=True,
                                    split_alphanumeric=False,
                                    lemmatize=False,
                                    stem=False))

    # predict
    pred, raw_outputs = model.predict(text)

    # convert to probability of risk
    prob = softmax(raw_outputs, axis=1)
    prob_risk = [x[1] for x in prob]
    pred_risk = [predicted_risk(x) for x in prob_risk]
    
    return pred, prob_risk, pred_risk


def predicted_risk(prob_risk):
    '''
    Calculate and output the predicted risk score of article/post

    Input: 
        prob_risk(arr): array consisting of probability of high risk
    Output:
        risk(float): predicted risk 

    '''
    risk = 100 * prob_risk
    return risk
