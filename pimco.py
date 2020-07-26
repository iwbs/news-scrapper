import requests
import time
import json
import os.path
from bs4 import BeautifulSoup
from pathlib import Path
from laser_checker import merge_sentence


ROOT_FOLDER = 'pimco'
DOMAIN = 'https://www.pimco.com.hk'

### Statistics ###
success_count = 0
fail_count = 0
failed_links = []
##################


def genJSON(text, folderPath):
    ary = []
    index_soup = BeautifulSoup(text, 'html.parser')
    header_section = index_soup.find('section', 'colFullWidth')
    if header_section is not None:
        if header_section.article is not None:
            if header_section.article.header is not None:
                if header_section.article.header.h1 is not None:
                    k = header_section.article.header.h1
                    title = k.get_text()
                    ary.append(title)
                    article = index_soup.find('article', 'articleDetail')
                    if article is not None:
                        p_ary = article.find_all('p')
                        for p in p_ary:
                            if p.get_text() != '':
                                ary.append(p.get_text())
    return ary


Path(ROOT_FOLDER).mkdir(parents=True, exist_ok=True)
f = open("pimcoIndex.json", encoding="utf8")
j = json.loads(f.read())
for r in j['results']:
    if r['DocumentTypeString'] == 'article':
        cn_ary = []
        en_ary = []
        folderPath = os.path.join(ROOT_FOLDER, r['Category'])
        Path(folderPath).mkdir(parents=True, exist_ok=True)
        zh_path = f"{DOMAIN}{r['DestinationUrl']}"
        art_id = zh_path.rsplit('/', 1)[1]
        zh_detail = requests.get(zh_path)
        if zh_detail.status_code == 200:
            cn_ary = genJSON(zh_detail.text, folderPath)
        en_path = zh_path.replace("/zh-hk/", "/en-hk/")
        en_detail = requests.get(en_path)
        if en_detail.status_code == 200:
            en_ary = genJSON(en_detail.text, folderPath)
        else:
            continue

        if len(en_ary) > 0 and len(cn_ary) > 0:
            cn_ary.pop()
            en_ary.pop()
            output = {
                'en': en_ary,
                'cn': cn_ary
            }

            if len(en_ary) != len(cn_ary):
                output = merge_sentence(output)
                if len(output['en']) == len(output['cn']):
                    fullPath = os.path.join(folderPath, art_id + ".json")
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
                fullPath = os.path.join(folderPath, art_id + ".json")
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
