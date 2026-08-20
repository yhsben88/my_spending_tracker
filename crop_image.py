'''
crop_image.py
Author: Hiu Sum Yuen
'''

def crop_total_region(image, total_bbox, scale = 3):
    ys = [point[1] for point in total_bbox]

    y1 = min(ys)
    y2 = max(ys)

    height = image.shape[0]

    y_padding = abs(y2 - y1) * scale

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

