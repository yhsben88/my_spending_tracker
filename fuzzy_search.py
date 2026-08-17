'''
fuzzy_search.py
Author: Hiu Sum Yuen
'''

from Levenshtein import distance
from monetary_check_utils import normalize_keyword
from word_check_utils import has_word_subtotal


def fuzzy_search(reader_list:list, dic:dict):
    best_distance = 2 
    best_bbox = None
    best_text = None
    best_confidence = 0

    for bbox, text, confidence in reader_list:
        text_lower = normalize_keyword(text.lower().strip(":;"))
        if has_word_subtotal(text_lower) and 2 <= best_distance:
            # if subtotal exists, we will not completely disregard it, but it holds less priority than if any keyword matching text can be formed.
            best_distance = 2 
            best_bbox = bbox
            best_text = text
            best_confidence = confidence

        for keyword, keyword_score in dic.items():

            distance_score = distance(text_lower, keyword)

            if distance_score <= 1 and distance_score <= best_distance:
                best_distance = distance_score
                best_bbox = bbox
                best_text = text
                best_confidence = confidence

    return best_bbox, best_text, best_confidence