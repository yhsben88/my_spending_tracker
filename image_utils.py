"""
image_utils.py
Authored by: Hiu Sum Yuen
"""

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

def save_image_to(source_path: Path, save_folder: str,image):
    try:
        filename = source_path.name
        save_folder = Path(save_folder)
        save_folder.mkdir(parents=True, exist_ok=True)

        save_path = save_folder / filename

        success = cv2.imwrite(save_path, image)
        if not success:
            raise IOError(f"Could not save image to {save_path}")

    except cv2.error as e:
        raise RuntimeError("Failed to preprocess image") from e
    
    return save_path

def crop_image_bottom_half(image):
    height, width = image.shape[:2]
    bottom_half = image[height // 2:, :]
    return bottom_half

def upscale_image(image, scale=3):
    return cv2.resize(
        image,
        None,
        fx=scale,
        fy=scale,
        interpolation=cv2.INTER_CUBIC
    )

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
        
    except cv2.error as e:
        raise RuntimeError("Failed to preprocess image") from e

    return threshold
