'''
monetary_check_utils.py
Author: Hiu Sum Yuen
'''

import re

def extract_money(text):
    pattern = r'\$?\s*\d+(?:[.,]\d{2})'

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return None

def normalize_keyword(text):
    replacements = {
        "0": "o",
        "1": "l",
        "|": "l",
        "]": "l",
        "[": "l",
        ")": "l",
        "(": "l",
    }

    text = text.lower()

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text
