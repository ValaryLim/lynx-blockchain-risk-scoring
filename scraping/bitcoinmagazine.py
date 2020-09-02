from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from datetime import datetime
import pandas as pd

def bitcoinmagazine_scrape(entity, start_date, end_date):  
    #Remove all ' ' characters in url
    entity = entity.replace(' ','+')

    #Get max page number
    url = 'https://bitcoinmagazine.com/page/' + str(1)+'?s=' + entity
    req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req)
    soup = BeautifulSoup(page, 'lxml')

    data = {'date_time':[], 'title':[], 'description':[], 'article_url':[], 'image_url':[], 'author':[], 'author_url':[]}

    max_page = 1
    res = soup.find('div',class_ = 'nav-links')
    if res != None:
        for i in res.find_all('a',class_ ='page-numbers'):
            try:
                max_page = int(i.text)
            except ValueError:
                break
    

    #Iterate through all the pages there are 
    for i in range(1,max_page+1):
        url = 'https://bitcoinmagazine.com/page/' + str(i)+'?s=' + entity
        req = Request(url , headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req)
        soup = BeautifulSoup(page, 'lxml')


        for res in soup.find_all('div', class_= 'small-12 medium-6 columns'):
            try:
                date = res.find('li', class_ ='post-date').text
                d = datetime.strptime(date, '%B %d, %Y')

                if d <= end_date and d >= start_date:

                    data['date_time'].append(d)

                    title = res.h5.a.text.lower()
                    data['title'].append(title)

                    article_url = res.h5.a['href']
                    data['article_url'].append(article_url)

                    description = res.p.text.lower()
                    data['description'].append(description)

                    author_a = res.find('aside',class_ = 'thb-post-bottom').a
                    author = author_a.text.lower()
                    data['author'].append(author)

                    author_url = author_a.get('href')
                    data['author_url'].append(author_url)

                    image_url = res.figure.img.get('src')
                    data['image_url'].append(image_url)
            except:
                continue


    df = pd.DataFrame(data)
    return df




################ Test ##################
##entity = 'binance'
##start_date = datetime(2020,1,1)
##end_date = datetime(2020,9,1)
##df = bitcoinmagazine_scrape(entity, start_date, end_date)
#########################################
##df.to_csv(r'file.csv')



