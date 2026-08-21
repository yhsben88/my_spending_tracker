'''
reconstruct_money.py
Author: Hiu Sum Yuen
'''

import re 
from bbox_utils import bbox_bounds, get_bbox_center, union_bbox
from monetary_check_utils import is_money, extract_money

TESTING = False


def reconstruct_money(candidate_bbox, candidate_text, reader_list):

    if extract_money(candidate_text):
        return candidate_bbox, candidate_text, 0

    # --------------------------------------------------
    # Try going LEFT
    # --------------------------------------------------

    left = find_left_bbox(
        candidate_bbox,
        reader_list
    )

    if left is not None:

        left_bbox, left_text, left_confidence = left

        combined = combine_money_bboxes(
            left_text,
            candidate_text
        )

        if combined is not None:

            combined_bbox = union_bbox(
                left_bbox,
                candidate_bbox
            )

            return combined_bbox, combined, left_confidence

    # --------------------------------------------------
    # Try going RIGHT
    # --------------------------------------------------

    right = find_right_bbox(
        candidate_bbox,
        reader_list
    )

    if right is not None:

        right_bbox, right_text, right_confidence = right

        combined = combine_money_bboxes(
            candidate_text,
            right_text
        )

        if combined is not None:

            combined_bbox = union_bbox(
                candidate_bbox,
                right_bbox
            )

            return combined_bbox, combined, right_confidence

    # --------------------------------------------------
    # Could not reconstruct
    # --------------------------------------------------

    print(
        "reconstruct_money() could not find a neighboring "
        "bbox that forms a monetary value."
    )

    return candidate_bbox, candidate_text, None


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


def find_left_bbox(target_bbox, reader_list):

    _, target_y1, _, target_y2 = bbox_bounds(target_bbox)
    target_x_center, target_y_center = get_bbox_center(target_bbox)

    closest_bbox = None
    closest_distance = float("inf")

    for bbox, text, confidence in reader_list:

        if bbox is target_bbox:
            continue

        _, y1, _, y2 = bbox_bounds(bbox)
        candidate_x_center, candidate_y_center = get_bbox_center(bbox)

        # Candidate must be horizontally to the LEFT
        if candidate_x_center >= target_x_center:
            continue

        # Candidate center must be inside target's vertical boundaries
        if not (target_y1 <= candidate_y_center <= target_y2):
            continue

        # Target center must be inside candidate's vertical boundaries
        if not (y1 <= target_y_center <= y2):
            continue

        # Find closest candidate to the left
        distance = target_x_center - candidate_x_center

        if distance < closest_distance:
            closest_distance = distance
            closest_bbox = (bbox, text, confidence)

    return closest_bbox


def combine_money_bboxes(left_text, right_text):

    match = re.fullmatch(
        r'[.,-]?(\d{2})',
        right_text.strip()
    )

    if match is None:
        return None

    left_text = left_text.rstrip('.,-')

    if not re.search(r'\d', left_text):
        return None

    cents = match.group(1)

    return f"{left_text}.{cents}"