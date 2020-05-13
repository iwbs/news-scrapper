import requests
import time
import json
import os.path
import re
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import quote


ROOT_FOLDER = 'ubs'
INDEX_JSON_FOLDER = 'ubs_json'


def genJSON(text):
    ary = []
    detail_soup = BeautifulSoup(text, 'html.parser')
    header = detail_soup.find('span', 'pageheadline__hl pageheadline__hl--leadtext')
    ary.append(header.text.strip())
    div = detail_soup.find('div', 'textimage__richtext textimage__richtext--noWrap textimage__listicon--bullet')
    for c in div.contents:
        if hasattr(c, 'get_text'):
            if c.name == 'ul':
                for li in c.contents:
                    if hasattr(li, 'get_text'):
                        t = li.get_text()
                        if len(t) > 0:
                            ary.append(t.strip())
            else:
                t = c.get_text()
                if len(t) > 0:
                    if t.startswith('• '):
                        ary.append(t[2:].strip())
                    elif t.startswith(' • '):
                        ary.append(t[3:].strip())
                    else:
                        ary.append(t.strip())

    if ary[-1].startswith('For more ') or ary[-1].startswith('Read more '):
        ary.pop()
    return ary


Path(ROOT_FOLDER).mkdir(parents=True, exist_ok=True)
for filename in os.listdir(INDEX_JSON_FOLDER):
    with open(os.path.join(INDEX_JSON_FOLDER, filename), encoding="utf8") as f:
        j = json.loads(f.read())
        for a in j['documents']:
            en_ary = []
            cn_ary = []
            f = a['fields']
            folderPath = os.path.join(ROOT_FOLDER, f["as_contentTypes"][0])
            Path(folderPath).mkdir(parents=True, exist_ok=True)
            art_id = f["aem_pageID"][0]
            zh_detail_url = f['targetOnlyContentUrl'][0]
            print(zh_detail_url)
            en_detail_url = zh_detail_url.replace('/tc/', '/en/')
            zh_detail = requests.get(zh_detail_url)
            if zh_detail.status_code == 200:
                cn_ary = genJSON(zh_detail.text)
            en_detail = requests.get(en_detail_url)
            if en_detail.status_code == 200:
                en_ary = genJSON(en_detail.text)
            if len(cn_ary) == len(en_ary):
                output = {
                    'en': en_ary,
                    'cn': cn_ary
                }
                fullPath = os.path.join(folderPath, art_id + ".json")
                with open(fullPath, 'w', encoding='utf8') as json_file:
                    json.dump(output, json_file, ensure_ascii=False, indent=4)
                print(f"{fullPath} created")
            else:
                print("discarded")