## Installations

`pip install opencv-python easyocr`

## references

OCR of choice,
[easyOCR](https://m-berta.medium.com/optical-character-recognition-ocr-pytesseract-vs-easyocr-5df810c6c91c)

# Lessons & Takeaways

## Preprocessing

- Understand how shadows and uneven lighting can affect image processing.
- Learn how Gaussian blur reduces noise and improves thresholding.
- Compare fixed thresholding with Otsu’s automatic thresholding for separating foreground from background.
- Improve image-processing robustness to varying lighting and shadows.

## Finding relevent data from the image

Using the correct reference point for our receipt total,

- Instead of machine learning our way into finding relevent positions for receipt totals. A simple heuristic evaluation became the idea to my answer for robustness.
- Receipts tend to put the final amount near the bottom, so among relevant labels, prefer the last one detected.

## UI/UX

- Visualize what the OCR sees to make scanning decisions easier to understand and debug.
- Show users processed images when scans fail, helping them identify issues such as poor lighting, glare, or distracting backgrounds.
- Provide clear guidance for improving image quality and preprocessing results.
  `cached idea, develop popup UI for poor user scans. To give tips on beeter scans.`
