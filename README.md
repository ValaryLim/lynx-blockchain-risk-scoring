# Blockchain Risk Scoring
#### *In collaboration with Lynx Analytics 


<br/>The Blockchain Risk Scoring project taps into open-source information to monitor the risk level of cryptocurrency entities on a daily basis. Open-source information utilised includes news articles from both conventional and crypto-specific sites, as well as social media posts from Reddit and Twitter.  While four different models were attempted, the final model used by the project is RoBERTa ([Robustly Optimized BERT Pretraining Approach](https://arxiv.org/abs/1907.11692)). We also built an additional layer upon the original neural network to cater to the context of risk scoring. Scored risks, both on a post and entity level, are eventually stored in a centralised database. In the future,  APIs will be created to query into the database for visualization purposes.

A more detailed breakdown of the project can be seen in the flowchart below.<br/>

  <br/>![image](https://i.postimg.cc/1X6LxnND/Screenshot-2020-11-01-at-1-34-31-PM.png)<br/>



## Getting Started

The end-user mainly makes use of the automation branch of the GitHub repository. A **requirements.txt** file is provided for the specification of the packages used in the project. The user can run the following command to install the packages.

```bash
pip install -r requirements.txt
```


## Usage

The entire data retrieval, risk scoring, and data storage pipeline of the project have been automated in the **auto_pipe.py** file. The user simply specifies the list of entities and the time period for the get_data_all function to complete the entire process. For example,

```python
from datetime import datetime

entities = ['binance','bitfinex', 'huobi', 'okex', 'upbit']
start = datetime(2020,9,1)
end = datetime(2020,10,26)
get_data_all(entities, start, end)
```
<br/>The **auto_pipe.py** file also provides a **train** function for the model to be re-trained when performance drops (or on a monthly basis depending on whichever is more suitable).  The **train** method automatically retrieves data from the database for re-training. Parameters that the **train** functions accepts are specified under the function itself. <br/>



## Database

Two databases are used to store post-level and entity-level data respectively. Specific columns within each database and sample queries on risk scores can be seen below.

  <br/>![image](https://i.postimg.cc/Jhb73TD5/Screenshot-2020-11-04-at-1-01-39-AM.png)<br/>



## Sample Visualisations

*Dashboard gifs to be added*


## Files

The main folder to be used is **automation**, which has combined the source code and automated the pipeline using the other folders.  

Here is a breakdown of the other folders,
<br>


|     Folder           |Function                                                                             |
|----------------------|-------------------------------------------------------------------------------------|
|**scraping**          |Scraping scripts for open source information, including news, Reddit and Twitter data|
|**sentiment-analysis**|Models attempted for risk scoring, including Bert, FastText, word2vec and Vader      |
|**evaluation**        |Evaluation of the better performing models - Bert, Roberta and word2vec on 2020 data |
|**scoring**           |Methods to assign risk scores to entities based on output from the model             |
|**demo**              |A sample visualisation built using python dash                                       |


scraping
--
Mains scripts in the **scraping** folder are: *main_conventional.py*, *main_crypto.py*, *reddit.py* and  *twitter_twint.py*. Note that the original *twitter.py* which uses the twitterscraper API may not be able to retrieve tweets due to [a known problem stated on its GitHub page](https://github.com/taspinar/twitterscraper/issues/339). 

Each scraping function takes in three arguments: entity, start date and end date, and returns the open source data within the stated date range for the particular entity. 

The rest of the scripts in the folder are website specific, such as *cryptonews.py*. These scripts are imported by the main scrapers. 


sentiment-analysis
--
Each of the four models attempted has additional files apart from the main one.

For Bert, the *bert_model_analysis.ipynb* was created to understand the model from various perspectives, including word cloud, word count and optimal threshold selection. 

For FastText, three models are attempted and the scripts are saved separately. *fasttext_offshelf.ipynb* uses pretrained models; *fasttext.ipynb* trains a model using our own labelled data;  *fasttext_preprocessing.ipynb* added preprocessing on top of *fasttext.ipynb*.

For Vader, *vader.py* contains the simple prediction code without performance evaluation. *vader_original_backtest.py* makes use of the original vader dictionary for sentiment scoring while *vader_custom_backtest.py* adds a list of customised words to the dictionary. 

For word2vec, *word2vec_improvements.ipynb* contains various methods attempted to improve the performance. The lime package is used to explain the word2vec model and the code can be found in *evaluation_lime.ipynb*.

Two additional evaluation notebooks were created to better understand word2vec, Bert and Roberta:

- *evaluation_textprocessing.ipynb*: looks into how each model handles transaction hashes and joint digits (eg, "40 million" vs "40million")
- *evaluation_wordrisk.ipynb*: tries to list out the most influential words for prediction for each model 

Notably, we have also tried to resolve the issue of an entity being wrongly tagged - the news mentioned this entity but the hack case was on another entity. However, the task proved to be too complicated and since such cases were rather rare, we took the issue as a limitation of the current model. The attempt can be found in *article_tagging.ipynb*. 

evaluation
--
The model performances were furtehr evaluated from the hack capturing perspective on 2020 data. 

We compare the percentage of posts being scored as high risk for each entity and check whether high percentage correponds to the empirical hack cases. For example, the graph for Binance can be seen below.


![binace](https://i.postimg.cc/PJxcSxxQ/Screenshot-2020-11-04-at-12-28-48-AM.png)

We can then compare to the real hacks reported for Binace,

> 2020-03-11 - Binance Users in Turkey May Have Been Compromised, Many Receive Phishing SMS Messages\
> 2020-04-07 - Binance Accused of Stealing $1 Million Worth of Assets: Company Denies Everything but Class Action Underway\
> 2020-04-29 - Binance ddos attack

This preliminary analysis on empirical performance is further developed with a precisely define risk scoring method across entities.

scoring
--
There are two files under this folder. 

The *scoring_exploration.ipynb* includes our initial exploration in order to decide on the risk scoring method from the raw model output. The values attempted, regarding risky posts, include daily count, percentage and weighted percentage (as certain posts appear more than once, especially for Reddit and Twitter). Decay was also tried to smoothen the curve. 

For the *scoring_final.ipynb*, we eventually decided to use weighted average with customised thresholds for different entities. Here is the sample output for Okex. The red dotted lines mark the actual hack cases. 

![okex.png](https://i.postimg.cc/635cVmjk/Screenshot-2020-11-04-at-12-49-22-AM.png)


demo
--
The demo folder contains a sample dashboard for the end user. For simplicity, we just took in data from two csv files with the same information structure as the database. The actual visualisations are covered in the section above. 


## Built With
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) 
- [Google BERT](https://github.com/google-research/bert)
- [Facebook fastText](https://fasttext.cc) 
- [word2vec](https://code.google.com/archive/p/word2vec/)
- [Natural Language Toolkit](https://www.nltk.org) 
- [lime](https://github.com/marcotcr/lime)
- [plotly | dash](https://dash.plotly.com)



## Authors
- Lai Yan Jean -  [Github](https://github.com/laiyanjean)
- Lee Jing Xuan - [Github](https://github.com/leejx9)
- Valary Lim Wan Qian - [Github](https://github.com/ValaryLim)
- Xu Pengtai - [Github](https://github.com/Pengtai9928)
