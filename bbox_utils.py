"""
bbox_utils.py
Authored by: Hiu Sum Yuen
"""

import cv2
import numpy as np

def find_word_total(reader_list: list): 
    total_bbox = None
    total_text = None
    best_score = -1

    keyword_scores = {
        "amount due": 5,
        "total due": 5,
        "total": 4,
        "amount": 3,
        "due": 2
    }

    for bbox, text, confidence in reader_list:
        text_lower = text.lower().strip(":;")

        score = 0

        for keyword, keyword_score in keyword_scores.items():
            if keyword in text_lower:
                score = max(score, keyword_score)

        if score >= best_score:
            best_score = score
            total_bbox = bbox
            total_text = text

    if total_bbox is None:
        raise ValueError("Cannot find any relevant words for Total.")

    return total_bbox, total_text, confidence

def bbox_bounds(bbox):
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]

    return min(xs), min(ys), max(xs), max(ys)

def get_bbox_center(bbox):
    x = sum(point[0] for point in bbox) / 4
    y = sum(point[1] for point in bbox) / 4
    return x, y


'''
Scoring:
    0: no relevent candidate could be found with the given reference box
    1: candidate is vertically overlapping reference box to the left
    2: candidate is overlapping reference box, vertically to the right | horizontally underneath
    5: candidate sits below, near the center of reference box, is bigger than reference box
    6: candidate sits below, near the center of reference box, shifted to the left
    7: candidate sits below, near the center of reference box,shifted to the right
    10: candidate sits to the right, near the center of reference box, candidate may be bigger | positioned higher than reference box
    13: candidate sits to the right, near the center of reference box, shifted below the reference box
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

        # Candidate is exclusively to the right of reference bbox
        if x1 >= ref_x2 and y1 <= ref_y_center <= y2:
            score += 11

        # Candidate exclusively vertically under reference bbox
        if ref_y2 <= y1 and x1 <= ref_x_center <= x2:
            score += 6

        # Candidate remotely overlaps vertically or horizontally under reference bbox, extra points for relevence
        if ref_y1 <= y1 <= ref_y2 or ref_x1 <= x1 <= ref_x2:
            score += 3 
        # Prioritizing relevence to the right than to the left
        elif ref_x1 < x2 < ref_x2:
            score += 2
        # if Candidate has no overlap and is at the bottom right of reference
        elif y1 >= ref_y2 and x1 >= ref_x2: 
            pass

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
    show_text = True
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