import stanza

f = open("11X11-Course-Project-Data/set1/a8.txt", "r", encoding="UTF-8")
article = f.read()
f.close()


nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,ner,constituency')

doc = nlp(article)

def uncap(s):
    if s == "I":
        return s
    return s[0].lower() + s[1:]

neg_words = ["not", "never", "n't"]
def binary_question(sentence, w):
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
            

def generate():
    for sentence in doc.sentences:
        tree = sentence.constituency.children[0].children
    
        if len(tree) != 3:
            continue
        if tree[0].label != "NP" or tree[1].label != "VP" or tree[2].label != ".":
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
                    question = binary_question(sentence, word.text)
                    if question != "":
                        print(question)
                        
generate()
            

        