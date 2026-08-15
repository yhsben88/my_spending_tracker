'''
find_word_total.py
Author: Hiu Sum Yuen
'''

from monetary_check_utils import normalize_keyword
from fuzzy_search import fuzzy_search
from fuzzy_search import is_subtotal


def find_word_total(reader_list: list): 
    total_bbox = None
    total_text = None
    best_score = 0
    best_confidence = 0

    keyword_scores = {
        "amount due": 5,
        "total due": 5,
        "total": 4,
        "amount": 3,
        "due": 2,
    }

    for bbox, text, confidence in reader_list:
        text_lower = text.lower().strip(":;")
        text_lower = normalize_keyword(text_lower)

        score = -1 # if final score is -1, the algorithm didn't get any text that match the dictionary.

        # Any variation of subtotal, we'd rather perform fuzzy search than take take a subtotal of any variation.
        if is_subtotal(text_lower):
            continue

        for keyword, keyword_score in keyword_scores.items():
            if " " in keyword:
                if keyword in text_lower:
                    score = max(score, keyword_score)
            else:
                if keyword in text_lower.split():
                    score = max(score, keyword_score)

        if score >= best_score:
            best_score = score
            total_bbox = bbox
            total_text = text_lower
            best_confidence = confidence
    if total_bbox is None:
        total_bbox, total_text, best_confidence = fuzzy_search(reader_list, keyword_scores)
    
    if total_bbox is None:
        raise ValueError("Cannot find any relevent words for Total.")
    return total_bbox, total_text, best_confidence