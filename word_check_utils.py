'''
word_check_utils.py
Author: Hiu Sum Yuen
'''

def has_word_subtotal(text):
    return "subtotal" in text.replace(" ", "")

def has_word_sub(text):
    return "sub" in text.replace(" ", "")

def has_word_total(text):
    return "total" in text.replace(" ", "")
