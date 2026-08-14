import easyocr
from utils import load_image
from utils import preprocess
from pathlib import Path

image_data_folder = Path("./ignorable/large-receipt-image-dataset-SRD")
for image_path in sorted(image_data_folder.glob("*.jpg"))[:10]:
    reader = easyocr.Reader(['en'])
    receipt = load_image(image_path)
    preprocessed_receipt = preprocess(receipt, image_path)
    result = reader.readtext(preprocessed_receipt)

    for detection in result:
        bbox, text, confidence = detection
        print(text, confidence)
    print("\n")