import stanza
import information as info

f = open("11X11-Course-Project-Data/set1/a8.txt", "r", encoding="UTF-8")
article = f.read()
f.close()
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,ner,constituency,lemma, depparse')

doc = nlp(article)


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

        
def generate():
    for sentence in doc.sentences:
        tree = sentence.constituency.children[0].children
    
        if tree[0].label != "NP" or tree[1].label != "VP":
            continue
        verb = tree[1].children[0].children[0]
        verb = str(verb)
        if len(sentence.words) > 15:
                continue
        for i, word in enumerate(sentence.words):
            if i == 0:
                continue
            prevTag = sentence.words[i - 1].upos
            if word.text == verb:
                if word.upos == "AUX" and (prevTag == "PROPN" or prevTag == "PRON" or prevTag == "NOUN"):
                    ques = binary_question_aux(sentence, word.text)
                elif word.feats != None:
                    ques = binary_question_compound(sentence, word.text)
                break
                                           
generate()
            

        