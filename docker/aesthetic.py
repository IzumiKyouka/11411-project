import string


def eliminate_space(question):
    if question is None: return
    i = 0
    while i < len(question):
        if i > 0 and question[i] in string.punctuation and question[i-1] == ' ':
            question = question[:i-1] + question[i:]
        i += 1
    return question

def capitalize_init(text):
    return text.capitalize()

def decapitalize_noninit(text):
    pass

def wrapping(text):
    text = capitalize_init(text)
    if text[-1] not in ['.', '!', '?']:
        text = text + '.'
    return text