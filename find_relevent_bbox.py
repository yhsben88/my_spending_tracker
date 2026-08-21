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
    Regions of interest with respect to reference point are, columns & rows
    c & r    0   1   2
        0   00  01  02 
        1   10  11  12
        2   20  21  22
        
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
                print(f"\t Is a monetary value")
        elif extract_money(text):
            score += 5 # specifically has to make the candidate worth more than position alone
            if DEV:
                HAS_MONEY = True
                print(f"\t Is a possible monetary value")


        # Reference bbox itself may contain the value, region [1][1]
        is_inside_ref_bbox = point_is_inside_bbox(ref_x_center, ref_y_center, bbox)
        if is_inside_ref_bbox:
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
        if x1 >= ref_x2: # if region in column [2]
            if y1 <= ref_y_center <= y2: # if region [1][2]
                score += 16
                if HAS_MONEY:
                    print(f"\tIs exclusively right & vertically centered")           
            elif ref_y1 < y2 and y1 < ref_y2: # if region between [1][2] & [2][2]
                score += 9
                if HAS_MONEY:
                    print(f"\tIs exclusively right & vertically close")

        # Candidate exclusively vertically under reference bbox, if region [2][1]
        if ref_y2 <= y1 and x1 <= ref_x_center <= x2: 
            score += 6
            if HAS_MONEY:
                print(f"\tIs exclusively below & horizontally centered")

        # Candidate overlaps vertically or horizontally, and does not count as sitting inside reference box, 
        # overlaps [1][1] but not counting as [1][1].
        if not is_inside_ref_bbox and ref_y1 <= ( y1 or y2 ) <= ref_y2 and (ref_x1 <= ( x1 or x2 ) <= ref_x2):
            score += 3 
            if HAS_MONEY:
                print(f"\tIs overlapping")
        
        # if Candidate has no overlap and sits in regions,
        #  [0][0], [0][2], [2][0], [2],[2]
        elif ref_x2 < x1 or x2 < ref_x1:
            if ref_y2 < y1: # region [2][0], [2],[2]
                score += 3
                if HAS_MONEY:
                    print(f"\t May be irrelavent, sits below reference")
            elif y2 < ref_y1: # region [0][0], [0][2]
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
