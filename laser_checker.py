from laserembeddings import Laser
import numpy as np

laser = Laser()

threshold = 0.83
zh_punctuation = ['。', '?', '!']
en_punctuation = ['.', '?', '!']

def calc_cos_sim(v1, v2):
    n1 = np.linalg.norm(v1)
    n2 = np.linalg.norm(v2)
    return np.dot(v1, v2) / n1 / n2

def append_full_stop(str, lang):
    hasFullStop = False
    if lang == 'zh':
        for p in zh_punctuation:
            if str.endswith(p):
                hasFullStop = True
                break
        if not hasFullStop:
            str += '。'
    else:
        for p in en_punctuation:
            if str.endswith(p):
                hasFullStop = True
                break
        if not hasFullStop:
            str += '.'
    return str
    
def merge_sentence(j):
    i = 0
    en_ary = j['en']
    cn_ary = j['cn']
    while i < len(en_ary) and i < len(cn_ary):
        zh_text = cn_ary[i]
        en_text = en_ary[i]
        embeddings = laser.embed_sentences([zh_text, en_text], lang=['zh', 'en'])
        cos_similarity = calc_cos_sim(embeddings[0], embeddings[1])
        euclidean_dist = np.linalg.norm(embeddings[0] - embeddings[1])
        if cos_similarity < threshold and i + 1 < len(en_ary) and i + 1 < len(cn_ary):
            base_sim = cos_similarity
            base_dist = euclidean_dist
            # try merge cn_ary[i] + cn_ary[i+1]
            zh_text = append_full_stop(cn_ary[i], 'zh') + cn_ary[i+1]
            en_text = en_ary[i]
            embeddings = laser.embed_sentences([zh_text, en_text], lang=['zh', 'en'])
            new_sim = calc_cos_sim(embeddings[0], embeddings[1])
            new_dist = np.linalg.norm(embeddings[0] - embeddings[1])
            if new_sim > base_sim and new_dist < base_dist:
                cn_ary[i] = zh_text
                cn_ary.remove(cn_ary[i+1])
                continue
            else:
                # try merge en_ary[i] + en_ary[i+1]
                zh_text = cn_ary[i]
                en_text = append_full_stop(en_ary[i], 'en') + ' ' + en_ary[i+1]
                embeddings = laser.embed_sentences([zh_text, en_text], lang=['zh', 'en'])
                new_sim = calc_cos_sim(embeddings[0], embeddings[1])
                new_dist = np.linalg.norm(embeddings[0] - embeddings[1])
                if new_sim > base_sim and new_dist < base_dist:
                    en_ary[i] = en_text
                    en_ary.remove(en_ary[i+1])
                    continue
        i += 1

    output = {
        'en': en_ary,
        'cn': cn_ary
    }
    return output

