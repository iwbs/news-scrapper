import requests
import time
import json
import os.path
from bs4 import BeautifulSoup
from pathlib import Path
from laser_checker import merge_sentence


ROOT_FOLDER = 'zeal'
next_article_link = ''

### Statistics ###
success_count = 0
fail_count = 0
failed_links = []
##################


def genJSON(article_link, folderPath, getTotalPage=False):
    global next_article_link
    global success_count
    global fail_count
    en_url = article_link
    cn_url = article_link.replace("/en-", "/cn-")
    art_id = article_link.split('/')[4][3:]
    en_article = requests.get(en_url)
    cn_article = requests.get(cn_url)
    if cn_article.status_code == 200 and en_article.status_code == 200:
        en_ary = []
        cn_ary = []
        sub_section_en = []
        sub_section_cn = []
        en_art_soup = BeautifulSoup(en_article.text, 'html.parser')
        cn_art_soup = BeautifulSoup(cn_article.text, 'html.parser')
        en_header = en_art_soup.find('h1', 'entry-title')
        cn_header = cn_art_soup.find('h1', 'entry-title')
        title_en = en_header.text
        title_cn = cn_header.text
        en_ary.append(title_en)
        cn_ary.append(title_cn)
        p_en = en_art_soup.find_all('p')
        p_cn = cn_art_soup.find_all('p')
        for i in range(len(p_en)):
            isTitle = p_en[i].find('strong')
            if isTitle:
                if len(sub_section_en) > 0:
                    en_ary.append(''.join(sub_section_en))
                    sub_section_en = []
                en_ary.append(p_en[i].text)
            else:
                sub_section_en.append(p_en[i].text)
        if sub_section_en[-1] == 'Disclaimer | Privacy Policy':
            sub_section_en.pop()
        en_ary.append(''.join(sub_section_en))
        for i in range(len(p_cn)):
            isTitle = p_cn[i].find('strong')
            if isTitle:
                if len(sub_section_cn) > 0:
                    cn_ary.append(''.join(sub_section_cn))
                    sub_section_cn = []
                cn_ary.append(p_cn[i].text)
            else:
                sub_section_cn.append(p_cn[i].text)
        if sub_section_cn[-1] == 'Disclaimer | Privacy Policy':
            sub_section_cn.pop()
        cn_ary.append(''.join(sub_section_cn))

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
                    'en': en_url,
                    'cn': cn_url,
                })
        else:
            fullPath = os.path.join(folderPath, art_id + ".json")
            with open(fullPath, 'w', encoding='utf8') as json_file:
                json.dump(output, json_file, ensure_ascii=False, indent=4)
            print(f"{fullPath} created")
            success_count += 1

        next_art = en_art_soup.find('a', rel='prev')
        if next_art:
            next_article_link = next_art.get('href')
        else:
            next_article_link = ''


# start scrapper
folderPath = ROOT_FOLDER
Path(folderPath).mkdir(parents=True, exist_ok=True)
# get first article from index
index = requests.get(f"https://www.zealasset.com/blog/en/")
if index.status_code == 200:
    index_soup = BeautifulSoup(index.text, 'html.parser')
    articles = index_soup.find_all('a', rel='bookmark')
    article_link = articles[0].get('href')
    genJSON(article_link, folderPath, getTotalPage=False)

    while next_article_link != '':
        genJSON(next_article_link, folderPath, getTotalPage=False)

    output = {
        'total': success_count + fail_count,
        'success': success_count,
        'fail': fail_count,
    }
    with open(f"{ROOT_FOLDER}_summary.json", 'w', encoding='utf8') as json_file:
        json.dump(output, json_file, ensure_ascii=False, indent=4)

    with open(f"{ROOT_FOLDER}_fail_list.json", 'w', encoding='utf8') as json_file:
        json.dump(failed_links, json_file, ensure_ascii=False, indent=4)
