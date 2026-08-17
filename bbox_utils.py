"""
bbox_utils.py
Authored by: Hiu Sum Yuen
"""

import cv2
import numpy as np


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

