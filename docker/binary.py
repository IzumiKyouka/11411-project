
def uncap(s):
    if s == "I":
        return s
    return s[0].lower() + s[1:]

neg_words = ["not", "never", "n't"]

def binary_question_aux(sentence, w):
    res = ""
    for i, word in enumerate(sentence.words):
        if word.text == w:
            if word.text == "'d":
                aux = "would"
            elif word.text == "'ve":
                aux = "have"
            elif word.text == "'m":
                aux = "am"
            elif word.text == "'re":
                aux = "are"
            else:
                aux = word.text
            res = aux.capitalize() + " " + res
        elif word.upos == "PROPN" or sentence.tokens[i].ner != "O":
            res += word.text + " "
        elif word.text in neg_words:
            continue
        elif word.text == "'" or word.text == "'s":
            res = res[:-1]
            res += word.text + " "
        else:
            res += uncap(word.text) + " "
    
    res = res[:-3]
    res += "?"
    return res

def dealFeats(features):
    res = 1
    for i in features:
        if "Tense" in i:
            if i == "Tense=Past":
                return 0
            elif i == "Tense=Pres":
                res = 1
        if "Person" in i:
            if i == "Person=3":
                return 2
    return res

def binary_question_compound(sentence, w):
    res = ""
    for i, word in enumerate(sentence.words):
        if word.text == w:
            res += word.lemma + " "
            features = word.feats.split("|")
            deal = dealFeats(features)
            if deal == 0:
                res = "Did " + res
            elif deal == 1:
                res = "Do " + res
            elif deal == 2:
                res = "Does " + res
        elif word.upos == "PROPN" or sentence.tokens[i].ner != "O":
            res += word.text + " "
        elif word.text in neg_words:
            continue
        elif word.text == "'" or word.text == "'s":
            res = res[:-1]
            res += word.text + " "
        else:
            res += uncap(word.text) + " "
    
    res = res[:-3]
    res += "?"
    return res

        

            

        