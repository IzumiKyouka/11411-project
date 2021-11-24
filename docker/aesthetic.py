import string


def eliminate_space(question):
    if question is None: return
    i = 0
    while i < len(question):
        if i > 0 and question[i] in string.punctuation and question[i-1] == ' ':
            question = question[:i-1] + question[i:]
        i += 1
    return question