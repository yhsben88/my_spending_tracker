import cv2
from pathlib import Path

def load_image(path: str): 
    '''
    Load an image
    '''
    image = cv2.imread(path)
    if image is None:
        raise FileNotFoundError(f"Could not find {image}")
    return image


def preprocess(image, path: Path) :
    if image is None:
         raise ValueError(f"Could not find {image}")
    try:
        # Convert the image to grayscale 
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Reduce noise
        gray = cv2.GaussianBlur(gray, (1, 1), 0)

        # Correct uneven lighting
        background = cv2.GaussianBlur(gray, (51, 51), 0)

        normalized = cv2.divide(
            gray,
            background,
            scale=255
        )

        # improve contrast
        _, threshold = cv2.threshold(
            normalized,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU # otsu method separates foreground from background.
        )
        filename = path.name
        save_processed_image_path = "./ignorable/training-data/" + filename
        success = cv2.imwrite(save_processed_image_path, threshold)
        if not success:
            raise IOError(f"Could not save image to {save_processed_image_path}")
        
    except cv2.error as e:
        raise RuntimeError("Failed to preprocess image") from e

    return threshold


