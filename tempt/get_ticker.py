import requests
from bs4 import BeautifulSoup

def get_ticker():
    url = 'https://stockanalysis.com/stocks/'
    html = requests.get(url)
    html.encoding = 'UTF-8'
    sp = BeautifulSoup(html.content, 'html5lib')

    script_tags = sp.find_all('script')[5]
    script_tag_lst = []
    for script_tag in script_tags:
        script_tag_lst.append(script_tag.get_text())
    script_tag_lst = script_tag_lst[0].split('\t')
    const_data = script_tag_lst[36].split('{s:')


    tickers = []
    for i in range(1,len(const_data)):
        d = const_data[i].split(',')
        tickers.append(d[0][1:-1])
    return tickers

