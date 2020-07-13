import requests
import time
import json
import os.path
import re
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import quote


ROOT_FOLDER = 'ubs'

### Statistics ###
success_count = 0
fail_count = 0
##################


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
f = open("ubs.json", encoding="utf8")
j = json.loads(f.read())
for a in j['hrefs']:
    en_ary = []
    cn_ary = []
    art_id = a.rsplit('/', 1)[1]
    art_id = art_id.rsplit('.')[1]
    zh_detail_url = a
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
        fullPath = os.path.join(ROOT_FOLDER, art_id + ".json")
        with open(fullPath, 'w', encoding='utf8') as json_file:
            json.dump(output, json_file, ensure_ascii=False, indent=4)
        print(f"{fullPath} created")
        success_count += 1
    else:
        print(f"{art_id} discarded")
        fail_count += 1

output = {
    'total': success_count + fail_count,
    'success': success_count,
    'fail': fail_count,
}
with open(f"{ROOT_FOLDER}_summary.json", 'w', encoding='utf8') as json_file:
    json.dump(output, json_file, ensure_ascii=False, indent=4)