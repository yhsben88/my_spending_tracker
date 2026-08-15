'''
find_relevent_bbox.py
Author: Hiu Sum Yuen
'''

from bbox_utils import bbox_bounds
from bbox_utils import get_bbox_center
from bbox_utils import point_is_inside_bbox
from bbox_utils import extract_money

def find_relevent_bbox(ref_bbox, reader_list) :
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
