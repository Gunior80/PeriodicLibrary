import re


def find_word(w):
    # Search words and phrases in text
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def get_words(periodic, text):
    # clear text construction. remove non-letters symbols and extra spaces in the text
    cleaned_text = re.sub(r'\s+', ' ', re.sub(r'[^\w\s-]', '', text)).strip()

    result = []
    for word in periodic.available_tags():
        if find_word(word)(cleaned_text):
            result.append(word)
    return result
