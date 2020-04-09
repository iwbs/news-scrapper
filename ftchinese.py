import requests
import time
import json
import os.path
from bs4 import BeautifulSoup
from pathlib import Path


ROOT_FOLDER = 'ftchinese'
categories = [
    {'name': 'stock', 'url': 'http://www.ftchinese.com/channel/stock.html'},
    {'name': 'forex', 'url': 'http://www.ftchinese.com/channel/forex.html'},
    {'name': 'bond', 'url': 'http://www.ftchinese.com/channel/bond.html'},
    {'name': 'commodity', 'url': 'http://www.ftchinese.com/channel/commodity.html'}
]
DOMAIN = 'http://www.ftchinese.com'
ARTICLE_URL_SUFFIX = '/ce?ccode=LanguageSwitch&archive'
FROM_PAGE = 1
TO_PAGE = 30
SLEEP_SEC = 2

pageNum = 1
totalPage = 1


def genJSON(text, folderPath, getTotalPage=False):
    global totalPage
    index_soup = BeautifulSoup(text, 'html.parser')
    articles = index_soup.find_all('a', class_='item-headline-link')
    for s in articles:
        article_link = s.get('href')
        prefix = article_link.split('?', 1)[0]
        art_id = prefix.split('/')[2]
        target_link = prefix + ARTICLE_URL_SUFFIX
        art = requests.get(DOMAIN + target_link)
        if art.status_code == 200:
            art_soup = BeautifulSoup(art.text, 'html.parser')
            en_ary = []
            cn_ary = []
            header = art_soup.find('h1', 'story-headline story-headline-large')
            if len(header) == 3:
                title_en = header.contents[0]
                title_cn = header.contents[2]
                en_ary.append(title_en)
                cn_ary.append(title_cn)
                p_en = art_soup.select('div.leftp > p')
                p_cn = art_soup.select('div.rightp > p')
                for idx in range(len(p_en)):
                    if p_en[idx].text != '' and p_cn[idx].text != '':
                        en_ary.append(p_en[idx].text)
                        cn_ary.append(p_cn[idx].text)
                output = {
                    'en': en_ary,
                    'cn': cn_ary
                }
                fullPath = os.path.join(folderPath, art_id + ".json")
                with open(fullPath, 'w', encoding='utf8') as json_file:
                    json.dump(output, json_file, ensure_ascii=False)
                print(f"{fullPath} created")
            else:
                print(f"no bilingual page for {art_id}")
        # don't want to flood the website
        time.sleep(SLEEP_SEC)
    print(f"[{c['name']}] page {pageNum} finished")

    if getTotalPage:
        pageination_anchors = index_soup.select('div.pagination-inner > a')
        totalPage = int(pageination_anchors[-2]['href'].split('=')[1])


# start scrapper
Path(ROOT_FOLDER).mkdir(parents=True, exist_ok=True)
for c in categories:
    pageNum = FROM_PAGE
    folderPath = os.path.join(ROOT_FOLDER, c['name'])
    Path(folderPath).mkdir(parents=True, exist_ok=True)
    index = requests.get(f"{c['url']}?page={pageNum}")
    if index.status_code == 200:
        genJSON(index.text, folderPath, True)
        pageNum += 1

        while pageNum <= totalPage and pageNum <= TO_PAGE:
            nIndex = requests.get(f"{c['url']}?page={pageNum}")
            if nIndex.status_code == 200:
                genJSON(nIndex.text, folderPath)
                pageNum += 1
