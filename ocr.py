"""
ocr.py
Authored by: Hiu Sum Yuen
"""

import easyocr
from image_utils import load_image , preprocess , upscale_image , save_image_to
from find_word_total import find_word_total
from find_relevent_bbox import find_relevent_bbox
from visualize_receipt import visualize_receipt
from crop_image import crop_total_region , transform_bbox_for_crop_and_scale
from monetary_check_utils import is_money
from reconstruct_money import reconstruct_money
from pathlib import Path

TESTING = False
DEV_MODE = True


starting_image = 126
current_image = 1000 + starting_image
poorly_scanned = []


image_data_folder = Path("./ignorable/large-receipt-image-dataset-SRD")
reader = easyocr.Reader(['en'])

for image_path in sorted(image_data_folder.glob("*.jpg"))[starting_image:starting_image+1]:
    try:

        receipt = load_image(image_path)
        preprocessed_receipt = preprocess(receipt, image_path)
        receipt_data = reader.readtext(preprocessed_receipt)

        if DEV_MODE:
            dev_image = visualize_receipt(image=receipt, receipt_data=receipt_data, debug = True)
            save_image_to(image_path, "./ignorable/processed-images/dev/errors/untouched", dev_image)

        total_word_bbox, total_word, total_confidence = find_word_total(receipt_data)

        scale = 5

        total_region, crop_y1 = crop_total_region(
            preprocessed_receipt,
            total_word_bbox,
            scale
        )

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

        if DEV_MODE:
            dev_image = visualize_receipt(image=total_region, receipt_data=total_region_data, debug = True)
            save_image_to(image_path, "./ignorable/processed-images/dev/errors/cropped/full", dev_image)
            dev_image = visualize_receipt(image=total_region, receipt_data=total_region_data, debug = False, reference_bbox=zoomed_total_bbox, reference_text=total_word_bbox)
            save_image_to(image_path, "./ignorable/processed-images/dev/errors/cropped/reduced", dev_image)


        value_score, value_bbox, value_text, value_confidence = find_relevent_bbox(
            zoomed_total_bbox,
            total_word,
            total_region_data
        )
        if value_bbox is None:
            raise ValueError(
                f"Could not locate a monetary value near '{total_word}'."
            )

        if not is_money(value_text.replace(" ", "")):
            if DEV_MODE:
                print(f"Running reconstruct_money with value_text: {value_text}")
            value_bbox, value_text, value_confidence = reconstruct_money(value_bbox, value_text, total_region_data)
            if value_text is None:
                raise ValueError(
                    f"Found a candidate near '{total_word}', "
                    f"but could not reconstruct a monetary value."
                )
            print(f"\n{current_image} is Flagged for needing reconstruction")
            
        print(f"{current_image}\n score: {value_score}\n Anchor word: {total_word}\n value: {value_text}\n confidence: {value_confidence}\n")




        debug_image_cropped = visualize_receipt(
            total_region,
            total_region_data,
            zoomed_total_bbox,
            total_word,
            value_bbox,
            value_text,
            debug=True,
            show_text= False,
        )
        save_image_to(image_path, "./ignorable/processed-images/user/cropped/full", debug_image_cropped)

        debug_image_cropped = visualize_receipt(
            total_region,
            total_region_data,
            zoomed_total_bbox,
            total_word,
            value_bbox,
            value_text,
            debug=False,
            show_text= False,
        )
        save_image_to(image_path, "./ignorable/processed-images/user/cropped/reduced", debug_image_cropped)
            

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
    