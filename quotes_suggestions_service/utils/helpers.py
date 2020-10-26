import re


def return_only_lower_letters(string: str):
    return re.sub('[^a-z]', '', string)
