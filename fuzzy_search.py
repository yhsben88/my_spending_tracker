'''
fuzzy_search.py
Author: Hiu Sum Yuen
'''

from Levenshtein import distance
from monetary_check_utils import normalize_keyword

def fuzzy_search(reader_list:list, dic:dict):
    # if best_distance stays at 2, then function will return None, None, 0
    best_distance = 2 
    best_bbox = None
    best_text = None
    best_confidence = 0

    for bbox, text, confidence in reader_list:
        text_lower = normalize_keyword(text.lower().strip(":;"))
        if "subtotal" in text_lower:
            continue

        for keyword, keyword_score in dic.items():

            distance_score = distance(text_lower, keyword)

            if distance_score <= 1 & distance_score <= best_distance:
                best_distance = distance_score
                best_bbox = bbox
                best_text = text
                best_confidence = confidence

    return best_bbox, best_text, best_confidence