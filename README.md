# Blockchain Risk Scoring
#### *In collaboration with Lynx Analytics 


<br/>The Blockchain Risk Scoring project taps into open-source information to monitor the risk level of cryptocurrency entities on a daily basis. Open-source information utilised includes news articles from both conventional and crypto-specific sites, as well as social media posts from Reddit and Twitter.  The raw model used by the project is Google's BERT, of which an additional layer is built upon the original neural network to cater to the context of risk scoring. Scored risks, both on a post and entity level, are eventually stored in a centralised database. In the future,  APIs will be created to query into the database for visualization purposes.

A more detailed breakdown of the project can be seen in the flowchart below.<br/>

  <br/>![image](https://i.postimg.cc/1X6LxnND/Screenshot-2020-11-01-at-1-34-31-PM.png)<br/>



## Getting Started

The end-user mainly makes use of the automation branch of the GitHub repository. A **requirements.txt** file is provided for the specification of the packages used in the project. The user can run the following command to install the packages.

```bash
pip install -r requirements.txt
```


## Usage

The entire data retrieval, risk scoring, and data storage pipeline of the project have been automated in the **auto_pipe.py** file. The user simply specifies the list of entities and the time period for the get_data function to complete the entire process.  For example,

```python
from datetime import datetime

entities = ['binance','bitfinex', 'huobi', 'okex', 'upbit']
start = datetime(2020,9,1)
end = datetime(2020,10,26)
get_data(entities, start, end)
```
<br/>The **auto_pipe.py** file also provides a **train** function for the model to be re-trained when performance drops (or on a monthly basis depending on whichever is more suitable).  The **train** method automatically retrieves data from the database for re-training. The only parameter to be specified is the filepath for the updated model to be stored at. <br/>



## Database

Two databases are used to store post-level and entity-level data respectively. Specific columns within each database and sample queries on risk scores can be seen below.

  <br/>![image](https://i.postimg.cc/3WQW7vfh/Screenshot-2020-11-01-at-2-21-36-PM.png)<br/>




## Sample Visualisations

*Dashboard gifs to be added*



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
