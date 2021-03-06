import requests
import time
import json
import os.path
from bs4 import BeautifulSoup
from bs4.element import Tag, Comment
from pathlib import Path
from laser_checker import merge_sentence


ROOT_FOLDER = 'allianz'

### Statistics ###
success_count = 0
fail_count = 0
failed_links = []
##################


def getContent(ele):
    ary = []
    for e in ele.contents:
        if isinstance(e, Tag):
            if e.name != 'style' and e.name != 'link' and e.name != 'a':
                sublist = getContent(e)
                for i in sublist:
                    ary.append(i)
        else:
            if not isinstance(e, Comment):
                a = e.strip()
                if len(a) > 1:
                    ary.append(a)
    return ary


def genJSON(text):
    index_soup = BeautifulSoup(text, 'html.parser')
    div = index_soup.select('section.editorial-page > div')
    if len(div) > 0:
        return getContent(div[0])
    else:
        return []


# start scrapper
Path(ROOT_FOLDER).mkdir(parents=True, exist_ok=True)
f = open("allianz.json", encoding="utf8")
j = json.loads(f.read())
for h in j['hrefs']:
    cn_ary = []
    en_ary = []
    art_id = h.rsplit('/', 1)[1]
    zh_path = h
    zh_detail = requests.get(zh_path)
    if zh_detail.status_code == 200:
        cn_ary = genJSON(zh_detail.text)
    en_path = h.replace("/zh-hk/", "/en/")
    en_detail = requests.get(en_path)
    if en_detail.status_code == 200:
        en_ary = genJSON(en_detail.text)

    output = {
        'en': en_ary,
        'cn': cn_ary
    }

    if len(en_ary) != len(cn_ary):
        output = merge_sentence(output)
        if len(output['en']) == len(output['cn']):
            fullPath = os.path.join(ROOT_FOLDER, art_id + ".json")
            with open(fullPath, 'w', encoding='utf8') as json_file:
                json.dump(output, json_file, ensure_ascii=False, indent=4)
            print(f"{fullPath} created")
            success_count += 1
        else:
            fail_count += 1
            failed_links.append({
                'id': art_id,
                'en': en_path,
                'cn': zh_path,
            })
    else:
        fullPath = os.path.join(ROOT_FOLDER, art_id + ".json")
        with open(fullPath, 'w', encoding='utf8') as json_file:
            json.dump(output, json_file, ensure_ascii=False, indent=4)
        print(f"{fullPath} created")
        success_count += 1


output = {
    'total': success_count + fail_count,
    'success': success_count,
    'fail': fail_count,
}
with open(f"{ROOT_FOLDER}_summary.json", 'w', encoding='utf8') as json_file:
    json.dump(output, json_file, ensure_ascii=False, indent=4)

with open(f"{ROOT_FOLDER}_fail_list.json", 'w', encoding='utf8') as json_file:
    json.dump(failed_links, json_file, ensure_ascii=False, indent=4)