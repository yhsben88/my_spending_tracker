'''
find_word_total.py
Author: Hiu Sum Yuen
'''

from monetary_check_utils import normalize_keyword
from fuzzy_search import fuzzy_search
from word_check_utils import has_word_total , has_word_sub
from bbox_utils import get_bbox_center, bbox_bounds

TESTING = False
DEBUG = False

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

    subtotal_parts = find_subtotal_bboxes(reader_list)

    for bbox, text, confidence in reader_list:
        text_lower = text.lower().strip(":;")
        text_lower = normalize_keyword(text_lower)

        # Any variation of subtotal, we'd rather perform fuzzy search than take take a subtotal of any variation.
        if has_word_sub(text_lower):
            continue

        # If target text is total AND previous text is subtotal, allow target to score IF relationship is vertical, not horizontal
        if has_word_total(text_lower):
            if is_part_of_subtotal(bbox, subtotal_parts):
                continue

        score = -1 # if final score is -1, the algorithm didn't get any text that match the dictionary.

        for keyword, keyword_score in keyword_scores.items():
            if " " in keyword:
                if keyword in text_lower:
                    score = max(score, keyword_score)
            else:
                if keyword in text_lower:
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

def find_subtotal_bboxes(reader_list):
    """
    Find OCR bounding boxes that appear to represent
    the 'sub' portion of a horizontally separated 'sub total'.

    Returns:
        list of bounding boxes containing 'sub'
    """
    subtotal_parts = []
    if DEBUG:
        print(f"\tlist of subtotal: ")

    for bbox, text, confidence in reader_list:
        text_lower = normalize_keyword(text.lower().strip(":;"))

        if has_word_sub(text_lower):
            subtotal_parts.append(bbox)
            if DEBUG:
                    print(f"\t[{text}] ")

    return subtotal_parts

def is_part_of_subtotal(candidate_bbox, subtotal_parts):
    """
    Determine whether candidate_bbox is the 'total' portion
    of a horizontally separated 'sub total'.
    """

    candidate_x1, candidate_y1, candidate_x2, candidate_y2 = \
        bbox_bounds(candidate_bbox)

    candidate_y_center = get_bbox_center(candidate_bbox)[1]

    for sub_bbox in subtotal_parts:
        sub_x1, sub_y1, sub_x2, sub_y2 = bbox_bounds(sub_bbox)

        sub_y_center = get_bbox_center(sub_bbox)[1]

        # Must be horizontally aligned
        vertically_aligned = (
            sub_y1 <= candidate_y_center <= sub_y2
            or
            candidate_y1 <= sub_y_center <= candidate_y2
        )

        # "total" should be to the right of "sub"
        horizontally_after = sub_x1 < candidate_x1

        if vertically_aligned and horizontally_after:
            return True

    return False
