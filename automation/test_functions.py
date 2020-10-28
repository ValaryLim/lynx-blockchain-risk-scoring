import sqlite3
from pprint import pprint
import datetime as datetime
import pandas as pd
import numpy as np


def get_articles_entity(entity_name, start_date, end_date):
    conn = sqlite3.connect('lynx_data.db')
    c = conn.cursor()

    c.execute('''
    SELECT * FROM POST_DATA
    WHERE (entity = ? AND (article_date BETWEEN ? AND ?))
    ORDER BY predicted_risk DESC
    ''', (entity_name, start_date, end_date))

    #pprint(c.fetchmany(10))
    df = pd.DataFrame(c.fetchall(), columns = ['uid', 'sourceID', 'source','article_date','content', 'url', 'count',\
                    'img_link','entity','author','ground_truth_risk','probability_risk','predicted_risk','coin']) 
    
    df.to_csv(r'~/Desktop/test.csv', index= False)
    conn.close()
    
    return

get_articles_entity('okex', '2020-10-19', '2020-10-26')

# c.execute('''
#     SELECT source, article_date, content, entity
#     FROM POST_DATA
#     WHERE ground_truth_risk = 0
# ''')
# pprint(c.fetchall())
# print()
# print('########################################################################')
# print()

# c.execute('''
#     SELECT * 
#     FROM ENTITY_DATA
#     WHERE entity = 'huobi'
# ''')
# pprint(c.fetchall())

