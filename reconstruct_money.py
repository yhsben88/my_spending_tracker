'''
reconstruct_money.py
Author: Hiu Sum Yuen
'''
import re
from bbox_utils import bbox_bounds
from bbox_utils import get_bbox_center
from monetary_check_utils import is_money , extract_money

TESTING = False


def reconstruct_money(candidate_bbox, candidate_text, reader_list):
    current_bbox = candidate_bbox
    current_text = candidate_text

    while True:
        if extract_money(current_text) or is_money(current_text): 
            # by returning zero confidence we are telling the user a right box is never used.
            return current_bbox, current_text, 0 

        right = find_right_bbox(
            current_bbox,
            reader_list
        )

        if right is None:
            return None, None, None

        right_bbox, right_text, right_confidence = right

        combined = combine_money_bboxes(
            current_text,
            right_text
        )

        if combined is not None:
            return right_bbox, combined, right_confidence

        current_bbox = right_bbox
        current_text = right_text

def find_right_bbox(target_bbox, reader_list):
    _, target_y1, _, target_y2 = bbox_bounds(target_bbox)
    target_x_center, target_y_center = get_bbox_center(target_bbox)

    closest_bbox = None
    closest_distance = float("inf")

    for bbox, text, confidence in reader_list:
        if bbox is target_bbox:
            continue

        _, y1, _, y2 = bbox_bounds(bbox)
        candidate_x_center, candidate_y_center = get_bbox_center(bbox)

        # Candidate must be horizontally to the right
        if candidate_x_center <= target_x_center:
            continue

        # Candidate center must be inside target's vertical boundaries
        if not (target_y1 <= candidate_y_center <= target_y2):
            continue

        # Target center must be inside candidate's vertical boundaries
        if not (y1 <= target_y_center <= y2):
            continue

        # Find closest candidate to the right
        distance = candidate_x_center - target_x_center

        if distance < closest_distance:
            closest_distance = distance
            closest_bbox = (bbox, text, confidence)

    return closest_bbox

def combine_money_bboxes(left_text, right_text):
    match = re.fullmatch(r'[.,-]?(\d{2})', right_text.strip())

    if match is None:
        return None

    left_text = left_text.rstrip('.,-')

    if not re.search(r'\d', left_text):
        return None

    cents = match.group(1)

    return f"{left_text}.{cents}"

