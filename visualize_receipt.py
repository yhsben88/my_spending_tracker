'''
visualize_receipt.py
Author: Hiu Sum Yuen
'''

from bbox_utils import draw_bbox

def visualize_receipt(
    image,
    receipt_data,
    reference_bbox = None,
    reference_text = "",
    value_bbox = None,
    value_text = "",
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
    if reference_bbox is not None:
        if show_text:
            draw_bbox(
                output,
                reference_bbox,
                f"REFERENCE: {reference_text}"
            )
        else:
            draw_bbox(
                output,
                reference_bbox
            )

    if value_bbox is not None:
        if show_text:
            draw_bbox(
                output,
                value_bbox,
                f"VALUE: {value_text}"
            )
        else:
            draw_bbox(
                output,
                value_bbox
            )

    return output
