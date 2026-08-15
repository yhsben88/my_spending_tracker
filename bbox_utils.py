"""
bbox_utils.py
Authored by: Hiu Sum Yuen
"""

import cv2
import numpy as np
from monetary_check_utils import extract_money
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

def bbox_bounds(bbox):
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]

    return min(xs), min(ys), max(xs), max(ys)

def get_bbox_center(bbox):
    x = sum(point[0] for point in bbox) / 4
    y = sum(point[1] for point in bbox) / 4
    return x, y

def point_is_inside_bbox(x, y, bbox):
    x1, y1, x2, y2 = bbox_bounds(bbox)

    return x1 <= x <= x2 and y1 <= y <= y2

'''
Scoring:
    0: no relevent candidate could be found with the given reference box
    1: candidate is vertically overlapping reference box to the left
    2: candidate is overlapping reference box, vertically to the right | horizontally underneath
    5: candidate sits below, near the center of reference box, is bigger than reference box
    6: candidate sits below, near the center of reference box, shifted to the left
    7: candidate sits below, near the center of reference box,shifted to the right
    10: candidate sits to the right, near the center of reference box, candidate may be bigger | positioned higher than reference box
    15: candidate is part of the reference bbox
    16: candidate is exclusively to the right of reference box and sitting vertically higher than reference box
    17: candidate sits to the right, near the center of reference box, shifted below the reference box
'''
def find_relevent_bbox(ref_bbox, reader_list) :
    ref_x1, ref_y1, ref_x2, ref_y2 = bbox_bounds(ref_bbox)
    ref_x_center, ref_y_center = get_bbox_center(ref_bbox)
    top_score = 0
    top_text = str
    top_confidence = 0
    top_bbox = None

    for bbox, text, confidence in reader_list:
        x1, y1, x2, y2 = bbox_bounds(bbox)
        score = -1

        # Reference bbox itself may contain the value
        if point_is_inside_bbox(ref_x_center, ref_y_center, bbox):
            if (t := extract_money(text)) is not None:
                top_score = 15
                top_text = t
                top_confidence = confidence
                top_bbox = bbox
                continue
            
        # Candidate is exclusively to the right of reference bbox
        if x1 >= ref_x2:
            if y1 <= ref_y_center <= y2:
                score += 11
            elif ref_y1 < y2:
                score += 10

        # Candidate exclusively vertically under reference bbox
        if ref_y2 <= y1 and x1 <= ref_x_center <= x2:
            score += 6

        # Candidate remotely overlaps vertically or horizontally under reference bbox, extra points for relevence
        if ref_y1 <= y1 <= ref_y2 or (ref_x1 <= x1 <= ref_x2 and ref_y1 <= y2):
            score += 3 
        # Prioritizing relevence to the right than to the left
        elif ref_x1 < x2 < ref_x2 and ref_y2 <= y2:
            score += 2
        # if Candidate has no overlap and is at the bottom right of reference
        elif y1 >= ref_y2 and x1 >= ref_x2: 
            pass

        # Prefer candidates with numeric-looking text
        if any(char.isdigit() for char in text):
            score += 6

        if score > top_score:
            top_score = score
            top_text = text
            top_confidence = confidence
            top_bbox = bbox

    return (top_score, top_bbox, top_text, top_confidence)

def draw_bbox(image, bbox, label=None):
    points = np.array(bbox, dtype=np.int32)

    cv2.polylines(
        image,
        [points],
        isClosed=True,
        color=(0, 255, 0),
        thickness=2
    )

    if label:
        x = int(min(point[0] for point in bbox))
        y = int(min(point[1] for point in bbox))

        cv2.putText(
            image,
            label,
            (x, y - 5),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    return image

def visualize_receipt(
    image,
    receipt_data,
    reference_bbox,
    reference_text,
    value_bbox,
    value_text = None,
    debug=False,
    show_text = False # show even more information that information overlaps
):
    output = image.copy()

    if debug:
        for bbox, text, confidence in receipt_data:
            draw_bbox(
                output,
                bbox,
                f"{text} ({confidence:.2f})"
            )
    if show_text == True:
        draw_bbox(
            output,
            reference_bbox,
            f"REFERENCE: {reference_text}"
        )

        draw_bbox(
            output,
            value_bbox,
            f"VALUE: {value_text}"
        )
    else:
        draw_bbox(
            output,
            reference_bbox
        )

        draw_bbox(
            output,
            value_bbox
        )

    return output

def crop_total_region(image, total_bbox):
    ys = [point[1] for point in total_bbox]

    y1 = min(ys)
    y2 = max(ys)

    height = image.shape[0]

    y_padding = abs(y2 - y1) * 2

    crop_y1 = max(0, y1 - y_padding)
    crop_y2 = min(height, y2 + y_padding)

    cropped = image[crop_y1:crop_y2, :]

    return cropped, crop_y1

def transform_bbox_for_crop_and_scale(bbox,vertical_displacement,scale=3):
    transformed_bbox = []

    for x, y in bbox:
        new_x = x * scale
        new_y = (y - vertical_displacement) * scale

        transformed_bbox.append([new_x, new_y])

    return transformed_bbox