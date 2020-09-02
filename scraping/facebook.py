import pandas as pd
from datetime import datetime
from facebook_scraper import get_posts

def facebook_scrape(entity, start_date, end_date):
    column_names = ['date_time', 'title', 'article_url']
    
    output = pd.DataFrame(columns = column_names)

    posts = get_posts(entity, pages = 10000)

    for post in posts:
        date_time = post['time']
        title = post['text']
        article_url = post['post_url']

        # add to dataframe if date is within range
        if (date_time != None):
            if ((date_time >= start_date) and (date_time <= end_date)):
                output = output.append({'date_time': date_time, 'title': title, \
                                        'article_url': article_url}, \
                                        ignore_index = True)
            
            # terminating condition
            if (date_time <= start_date):
                break
    
    return output

# testing function
# start_date = datetime(2020, 8, 26)
# end_date = datetime(2020, 8, 30)
# test = facebook_scrape('binance', start_date, end_date)
# print(test)