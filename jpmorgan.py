import requests
import time
import json
import os.path
from bs4 import BeautifulSoup
from pathlib import Path


ROOT_FOLDER = 'jpmorgan'
DOMAIN = 'https://am.jpmorgan.com'
INDEX = 'https://am.jpmorgan.com/hk/zh/asset-management/per/insights/investment-ideas/'

### Statistics ###
success_count = 0
fail_count = 0
##################

def cleanText(text):
    return text.replace('\u200b', '').replace('\n', '').replace('\r', '').replace('\xa0', ' ').strip()

def genJSON(article_link, folderPath, getTotalPage=False):
    global success_count
    global fail_count
    cn_url = article_link
    en_url = article_link.replace("/zh/", "/en/")
    art_id = article_link.split('/')[7]
    en_article = requests.get(f"{DOMAIN}{en_url}")
    cn_article = requests.get(f"{DOMAIN}{cn_url}")
    if cn_article.status_code == 200 and en_article.status_code == 200:
        en_ary = []
        cn_ary = []
        en_art_soup = BeautifulSoup(en_article.text, 'html.parser')
        cn_art_soup = BeautifulSoup(cn_article.text, 'html.parser')
        en_banner = en_art_soup.find('div', 'jpm-am-general-hero-banner')
        cn_banner = cn_art_soup.find('div', 'jpm-am-general-hero-banner')
        en_header = en_banner.find('h2')
        cn_header = cn_banner.find('h2')
        title_en = cleanText(en_header.text)
        title_cn = cleanText(cn_header.text)
        en_ary.append(title_en)
        cn_ary.append(title_cn)
        div_en = en_art_soup.find_all('div', 'jp-rft')
        div_cn = cn_art_soup.find_all('div', 'jp-rft')
        for d in div_en:
            for c in d.contents:
                if hasattr(c, 'text'):
                    caption = c.find('span', 'jp-rft_caption')
                    legal = c.find('span', 'jp-rft_legal')
                    if not caption and not legal:
                        txt = cleanText(c.text)
                        if len(txt) > 0 and txt != 'Explore our investment solutions':
                            en_ary.append(txt)
        for d in div_cn:
            for c in d.contents:
                if hasattr(c, 'text'):
                    caption = c.find('span', 'jp-rft_caption')
                    legal = c.find('span', 'jp-rft_legal')
                    if not caption and not legal:
                        txt = cleanText(c.text)
                        if len(txt) > 0 and txt != '了解我們的投資方案':
                            cn_ary.append(txt)
        if len(en_ary) == len(cn_ary):
            output = {
                'en': en_ary,
                'cn': cn_ary
            }
            fullPath = os.path.join(folderPath, art_id + ".json")
            with open(fullPath, 'w', encoding='utf8') as json_file:
                json.dump(output, json_file, ensure_ascii=False, indent=4)
            print(f"{art_id} created")
            success_count += 1
        else:
            print(f"Length not equal {art_id} en:{len(en_ary)} | cn:{len(cn_ary)}")
            fail_count += 1


# start scrapper
folderPath = ROOT_FOLDER
Path(folderPath).mkdir(parents=True, exist_ok=True)
# get first article from index
index = requests.get(INDEX)
if index.status_code == 200:
    index_soup = BeautifulSoup(index.text, 'html.parser')
    articles = index_soup.find_all('article', 'jp-card-text-img list-item bluebar')
    for article in articles:
        anchor = article.find('a')
        article_link = anchor.get('href')
        genJSON(article_link, folderPath, getTotalPage=False)

    output = {
        'total': success_count + fail_count,
        'success': success_count,
        'fail': fail_count,
    }
    with open(f"{ROOT_FOLDER}_summary.json", 'w', encoding='utf8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)
