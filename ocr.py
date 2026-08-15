"""
ocr.py
Authored by: Hiu Sum Yuen
"""

import easyocr
from image_utils import load_image
from image_utils import preprocess
from bbox_utils import find_word_total
from bbox_utils import find_relevent_bbox
from bbox_utils import visualize_receipt
from image_utils import save_image_to
from bbox_utils import crop_total_region
from image_utils import upscale_image
from bbox_utils import transform_bbox_for_crop_and_scale

from pathlib import Path

current_image = 1000
poorly_scanned = []
DEV_MODE = True

image_data_folder = Path("./ignorable/large-receipt-image-dataset-SRD")
reader = easyocr.Reader(['en'])

for image_path in sorted(image_data_folder.glob("*.jpg"))[:10]:
    try:

        receipt = load_image(image_path)
        preprocessed_receipt = preprocess(receipt, image_path)
        receipt_data = reader.readtext(preprocessed_receipt)

        total_word_bbox, total_word, total_confidence = find_word_total(receipt_data)

        total_region, crop_y1 = crop_total_region(
            preprocessed_receipt,
            total_word_bbox
        )

        scale = 3

        total_region = upscale_image(
            total_region,
            scale
        )

        total_region_data = reader.readtext(
            total_region
        )

        zoomed_total_bbox = transform_bbox_for_crop_and_scale(
            total_word_bbox,
            crop_y1,
            scale
        )

        value_score, value_bbox, value_text, value_confidence = find_relevent_bbox(
            zoomed_total_bbox,
            total_region_data
        )

        print(f"{current_image}\n score: {value_score}\n Anchor word: {total_word}\nvalue: {value_text}\n confidence: {value_confidence}\n")

        if DEV_MODE :
            debug_image = visualize_receipt(
                receipt,
                receipt_data,
                total_word_bbox,
                total_word,
                value_bbox,
                value_text,
                debug=True
            )
            save_image_to(image_path, "./ignorable/processed-images/dev/full", debug_image)

            debug_image_cropped = visualize_receipt(
                            total_region,
                            total_region_data,
                            zoomed_total_bbox,
                            total_word,
                            value_bbox,
                            value_text,
                            debug=True,
                            show_text= False
                        )
            save_image_to(image_path, "./ignorable/processed-images/dev/cropped", debug_image_cropped)
            

        user_image = visualize_receipt(
            receipt,
            receipt_data,
            total_word_bbox,
            total_word,
            value_bbox,
            value_text,
            debug=False,
            show_text= False
        )
        save_image_to(image_path, "./ignorable/processed-images/user/normal", user_image)

        user_image_threshold = visualize_receipt(
                    preprocessed_receipt,
                    receipt_data,
                    total_word_bbox,
                    total_word,
                    value_bbox,
                    value_text,
                    debug=False
                )
        save_image_to(image_path, "./ignorable/processed-images/user/threshold", user_image_threshold)

    except ValueError as e:
        # Specifically catches cases where "total" couldn't be found
        poorly_scanned.append({
            "image_number": current_image,
            "filename": image_path.name,
            "reason": str(e)
        })

    except Exception as e:
        # Catches unexpected errors so one bad image doesn't stop the dataset
        poorly_scanned.append({
            "image_number": current_image,
            "filename": image_path.name,
            "reason": str(e)
        })

    current_image += 1

print("\n========== SCAN SUMMARY ==========")

if poorly_scanned:
    print(f"{len(poorly_scanned)} image(s) could not be processed:\n")

    for image in poorly_scanned:
        print(
            f"Image {image['image_number']} "
            f"({image['filename']}): {image['reason']}"
        )
else:
    print("All images were successfully processed!")