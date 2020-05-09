import requests
import time
import json
import os.path
import re
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import quote


ROOT_FOLDER = 'fidelity'
categories = [
    {'name': 'inspiration-and-ideas',
        'url': 'https://www.fidelity.com.hk/zh/insights-and-updates/inspiration-and-ideas',
        'api': 'https://www.fidelity.com.hk/api/ce/content/Articles.json?template=ArticlesShort&maxResults=500&types=InspirationAndIdeas&countries=hk&country=hk&languages=zh%2Cen&language=zh&channels=ce.private-investor%2Cce.professional-investor%2Cce.professional-investor.fund-buyer%2Cce.professional-investor.fund-seller&channel=ce.professional-investor.fund-buyer'
     },
    {'name': 'investment-spotlight',
        'url': 'https://www.fidelity.com.hk/zh/insights-and-updates/investment-spotlight',
        'api': 'https://www.fidelity.com.hk/api/ce/content/Articles.json?template=ArticlesShort&maxResults=500&types=InvestmentSpotlight&countries=hk&country=hk&languages=zh%2Cen&language=zh&channels=ce.private-investor%2Cce.professional-investor%2Cce.professional-investor.fund-buyer%2Cce.professional-investor.fund-seller&channel=ce.professional-investor.fund-buyer'
     }
]
ARTICLE_API_PATH = 'https://www.fidelity.com.hk/api/ce/content/Articles.json?ids='
ARTICLE_API_PARAMS = '&countries=hk&country=hk&channels=ce.private-investor%2Cce.professional-investor%2Cce.professional-investor.fund-buyer%2Cce.professional-investor.fund-seller&channel=ce.professional-investor.fund-buyer'
ARTICLE_API_ZH_PARAMS = '&languages=zh%2Cen&language=zh'
ARTICLE_API_EN_PARAMS = '&languages=en%2Czh&language=en'
SLEEP_SEC = 2


def genJSON(text, folderPath):
    index = json.loads(text)
    for i in index:
        headline = i['content']['headline']
        article_path = i['metadata']['id']
        art_id = article_path.split('/')[1]
        encoded_path = quote(article_path, safe='')
        h = re.findall(r'[\u4e00-\u9fff]+', headline)
        if len(h) != 0 and '只備英文版' not in headline:
            zh_article = requests.get(
                f"{ARTICLE_API_PATH}{encoded_path}{ARTICLE_API_PARAMS}{ARTICLE_API_ZH_PARAMS}")
            en_article = requests.get(
                f"{ARTICLE_API_PATH}{encoded_path}{ARTICLE_API_PARAMS}{ARTICLE_API_EN_PARAMS}")
            if zh_article.status_code == 200 and en_article.status_code == 200:
                en_ary = []
                cn_ary = []

                zh_json = json.loads(zh_article.text)
                zh_panels = zh_json[0]['content']['panels']
                zh_headline = zh_panels[0]['configuration']['left']['headline']['text']
                cn_ary.append(zh_headline)
                zh_content = zh_panels[1]['configuration']['paragraphs'][0]['text']
                zh_soup = BeautifulSoup(zh_content, 'html.parser')
                zc = zh_soup.contents
                for k in list(zc):
                    if k == ' ' or k.text == '\xa0':
                        zc.remove(k)

                en_json = json.loads(en_article.text)
                en_panels = en_json[0]['content']['panels']
                en_headline = en_panels[0]['configuration']['left']['headline']['text']
                en_ary.append(en_headline)
                en_content = en_panels[1]['configuration']['paragraphs'][0]['text']
                en_soup = BeautifulSoup(en_content, 'html.parser')
                ec = en_soup.contents
                for k in list(ec):
                    if k == ' ' or k.text == '\xa0':
                        ec.remove(k)

                if len(zc) == len(ec):
                    for i in range(len(zc)):
                        zh_c_soup = BeautifulSoup(
                            zc[i].text, 'html.parser')
                        zh_c_strings = list(zh_c_soup.strings)
                        en_c_soup = BeautifulSoup(
                            ec[i].text, 'html.parser')
                        en_c_strings = list(en_c_soup.strings)
                        if len(zh_c_strings) == len(en_c_strings):
                            for j in range(len(zh_c_strings)):
                                c = zh_c_strings[j].strip().replace(
                                    '<br/>', '')
                                if len(c) != 0:
                                    cn_ary.append(c)
                                c = en_c_strings[j].strip().replace(
                                    '<br/>', '')
                                if len(c) != 0:
                                    en_ary.append(c)
                    if len(cn_ary) == len(en_ary):
                        output = {
                            'en': en_ary,
                            'cn': cn_ary
                        }
                        fullPath = os.path.join(folderPath, art_id + ".json")
                        with open(fullPath, 'w', encoding='utf8') as json_file:
                            json.dump(output, json_file, ensure_ascii=False)
                        print(f"{fullPath} created")
                    else:
                        print(
                            f'Inner Array len not match! Discard article - {zh_headline}')
                else:
                    print(
                        f'Array len not match! Discard article - {zh_headline}')
            # time.sleep(SLEEP_SEC)


Path(ROOT_FOLDER).mkdir(parents=True, exist_ok=True)
for c in categories:
    folderPath = os.path.join(ROOT_FOLDER, c['name'])
    Path(folderPath).mkdir(parents=True, exist_ok=True)
    index = requests.get(f"{c['api']}")
    if index.status_code == 200:
        genJSON(index.text, folderPath)
