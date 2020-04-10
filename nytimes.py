import requests
import time
import json
import os.path
from bs4 import BeautifulSoup
from pathlib import Path


ROOT_FOLDER = 'nytimes'
categories = [
    {'name': 'global-ec', 'url': 'https://cn.nytimes.com/global-ec/'},
    {'name': 'china-ec', 'url': 'https://cn.nytimes.com/china-ec/'},
    {'name': 'dealbook', 'url': 'https://cn.nytimes.com/dealbook/'}
]
DOMAIN = 'https://cn.nytimes.com'
ARTICLE_URL_SUFFIX = 'dual/'
FROM_PAGE = 1
TO_PAGE = 50
SLEEP_SEC = 2

pageNum = 1
hasMorePage = False


def genJSON(text, folderPath):
    global hasMorePage
    index_soup = BeautifulSoup(text, 'html.parser')
    articles = index_soup.select('h3 > a')
    for s in articles:
        article_link = s.get('href')
        tks = article_link.split('/')
        art_id = f"{tks[1]}_{tks[2]}_{tks[3]}"
        art = requests.get(DOMAIN + article_link + ARTICLE_URL_SUFFIX)
        if art.status_code == 200:
            art_soup = BeautifulSoup(art.text, 'html.parser')
            en_ary = []
            cn_ary = []
            header = art_soup.select('div.article-header > header > h1')
            if len(header) == 2:
                title_cn = header[0].text
                title_en = header[1].text
                en_ary.append(title_en)
                cn_ary.append(title_cn)
                articles = art_soup.find_all(
                    'div', class_='row article-dual-body-item')
                articles.pop(0)
                for s in articles:
                    if len(s.contents) == 2:
                        p_en = s.contents[0].text
                        p_cn = s.contents[1].text
                        en_ary.append(p_en)
                        cn_ary.append(p_cn)
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

    nextBtn = index_soup.select('li.next')
    if len(nextBtn) == 1:
        hasMorePage = True
    else:
        hasMorePage = False


# start scrapper
Path(ROOT_FOLDER).mkdir(parents=True, exist_ok=True)
for c in categories:
    pageNum = FROM_PAGE
    folderPath = os.path.join(ROOT_FOLDER, c['name'])
    Path(folderPath).mkdir(parents=True, exist_ok=True)
    index = requests.get(f"{c['url']}{pageNum}/")
    if index.status_code == 200:
        genJSON(index.text, folderPath)
        pageNum += 1

        while hasMorePage and pageNum <= TO_PAGE:
            nIndex = requests.get(f"{c['url']}{pageNum}/")
            if nIndex.status_code == 200:
                genJSON(nIndex.text, folderPath)
                pageNum += 1
