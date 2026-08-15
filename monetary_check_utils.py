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
