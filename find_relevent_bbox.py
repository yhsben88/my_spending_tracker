'''
find_relevent_bbox.py
Author: Hiu Sum Yuen
'''

from bbox_utils import bbox_bounds
from bbox_utils import get_bbox_center
from bbox_utils import point_is_inside_bbox
from monetary_check_utils import money_relative_to_keyword , looks_like_date, is_money , extract_money

TESTING = False
DEV = False

def find_relevent_bbox(ref_bbox, ref_text, reader_list) :
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
    top_score = 1
    top_text = str
    top_confidence = 0
    top_bbox = None

    for bbox, text, confidence in reader_list:
        x1, y1, x2, y2 = bbox_bounds(bbox)
        score = 0

        if looks_like_date(text):
            continue

        HAS_MONEY = False
        if is_money(text):
            score += 6
            if DEV: 
                HAS_MONEY = True 
        elif extract_money(text):
            score += 5 # specifically has to make the candidate worth more than position alone
            if DEV:
                HAS_MONEY = True if DEV else False


        # Reference bbox itself may contain the value
        if point_is_inside_bbox(ref_x_center, ref_y_center, bbox):
            if (t := extract_money(text)) is not None:

                position = money_relative_to_keyword(text, ref_text)

                if position == "right":
                    score = 17
                    if HAS_MONEY:
                        print(f"\tIs in reference box to the right")

                elif position == "left":
                    score = 5
                    if HAS_MONEY:
                        print(f"\tIs in reference box to the left")

                else:
                    score = 8
                    if HAS_MONEY:
                        print(f"\tIs in reference box ambiguously")

                if score > top_score:
                    top_score = score
                    top_text = t
                    top_confidence = confidence
                    top_bbox = bbox

                continue
            
        # Candidate is exclusively to the right of reference bbox
        if x1 >= ref_x2:
            if y1 <= ref_y_center <= y2:
                score += 16
                if HAS_MONEY:
                    print(f"\tIs exclusively right & vertically centered")
            elif ref_y1 < y2 and y1 < ref_y2:
                score += 7
                if HAS_MONEY:
                    print(f"\tIs exclusively right & vertically close")
        # Candidate exclusively vertically under reference bbox
        if ref_y2 <= y1 and x1 <= ref_x_center <= x2:
            score += 6
            if HAS_MONEY:
                print(f"\tIs exclusively below & horizontally centered")

        # Candidate remotely overlaps vertically or horizontally under reference bbox, extra points for relevence
        if (ref_y1 <= y1 <= ref_y2 and ref_y2 <= y2 and (ref_x1 <= x1 <= ref_x2 or ref_x1 <= x2 <= ref_x2)) or (ref_x1 <= x1 <= ref_x2 and ref_y1 <= y2):
            score += 3 
            if HAS_MONEY:
                print(f"\tIs overlapping")
        
        # Candidate overlaps and sits to the left of reference bbox
        elif ref_x1 < x2 < ref_x2 and ref_y2 <= y2:
            score += 3
            if HAS_MONEY:
                print(f"\tIs overlapping below & slightly left")
        # if Candidate has no overlap 
        elif ref_x2 < x1 or x2 < ref_x1:
            if ref_y2 < y1:
                score += 3
                if HAS_MONEY:
                    print(f"\t May be irrelavent, sits below reference")
            elif y2 < ref_y1:
                score += 2
                if HAS_MONEY:
                    print(f"\t May be irrelavent, sits above the reference.")


        if DEV:
            if HAS_MONEY:
                print(f"\tscore is {score}\n\n")

        if score >= top_score:
            top_score = score
            top_text = text
            top_confidence = confidence
            top_bbox = bbox

    if top_bbox is None:
        raise ValueError(f"\n\tFound total anchor: {ref_text}\n\tThere is an issue with finding any monetary value box.")
                
    return (top_score, top_bbox, top_text, top_confidence)
