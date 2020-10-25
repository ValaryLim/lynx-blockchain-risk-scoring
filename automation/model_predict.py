from simpletransformers.classification import ClassificationModel, ClassificationArgs
from scipy.special import softmax

def model_predict(text):
    '''
    Takes in an array of text and returns predicted probability of risk.

    Input (arr): E.g. data[['content']]
    Output (arr): E.g. data['probability_risk'] = model_predict(data[['content']])
    '''
    # loading saved model, specifying same args as model init
    # model names: path to directory containing model files
        # model naming convention : roberta_YYYY_MM
    model_args = ClassificationArgs(num_train_epochs=2, learning_rate=5e-5)
    model = ClassificationModel(model_type = 'roberta', model_name = 'models/roberta_2020_10', \
                                args = model_args, use_cuda = False)

    # predict
    pred, raw_outputs = model.predict(text)
    # convert to probability of risk
    prob = softmax(raw_outputs, axis=1)
    prob_risk = [x[1] for x in prob]

    return prob_risk