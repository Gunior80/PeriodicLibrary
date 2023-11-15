import re


def edit_string_for_tags(tags):
    names = []
    for tag in tags:
        name = tag.name
        if "\n" in name or " " in name:
            names.append('%s' % name)
        else:
            names.append(name)
    return "\n".join(sorted(names))


def parse_tags(tagstring):
    cleaned_tagstring = re.sub(r'[^\w\s\n-]', '', tagstring)
    if not cleaned_tagstring:
        return []
    words = [w.strip() for w in cleaned_tagstring.split("\n")]
    words = list(set([re.sub(r'\s{2,}', ' ', w) for w in words if w]))
    words.sort()
    return words
