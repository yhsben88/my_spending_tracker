'''
monetary_check_utils.py
Author: Hiu Sum Yuen
'''

import re

DEV = False

def extract_money(text):
    pattern = r'\$?\s*\d+(?:\s*[.,-]\s*\d{2})'

    match = re.search(pattern, text)

    if match:
        if DEV:
            print(f"\textract_money: {match}")
        return match.group(0)
    if DEV:
        print(f"\textract_money: {text}")
    return None

def is_money(text):
    result = re.fullmatch(
        r'\$?\s*\d+(?:\s*[.,-]\s*\d{2})',
        text.strip()
    ) 
    if DEV:
        if result is not None:
            print(f"\tis_money: {result}")
    return result is not None

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

    text = text.lower().strip()

    for old, new in replacements.items():
        text = text.replace(old, new)

    return text


def money_relative_to_keyword(text, keyword):
    money_match = re.search(
        r'\$?\s*\d+(?:\s*[.,-]\s*\d{2})',
        text
    )

    keyword_match = re.search(
        re.escape(keyword),
        text,
        re.IGNORECASE
    )

    if money_match is None or keyword_match is None:
        return None

    if money_match.end() <= keyword_match.start():
        return "left"

    if money_match.start() >= keyword_match.end():
        return "right"

    return "overlap"