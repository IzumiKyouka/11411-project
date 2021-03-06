
import stanza

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')

article = "When did Christiano Ronaldo join Real Madrid?"
doc = nlp(article)


def rating(question):
    q_type = identify(question)
    if q_type is None: return 0
    elif not q_type: return 5
    else:
        tree = question.constituency
        dic = dict()
        # find subject, verb, object
        search_component(tree, dic)

        sentence = question

        # find location
        place = []
        for i in range(len(sentence.words)):
            word = sentence.words[i]
            tok = sentence.tokens[i]
            if ('ORG' in tok.ner) or ('GPE' in tok.ner) or ('LOC' in tok.ner):
                if word.deprel == 'obl' and is_main_verb(sentence.words[word.head - 1]):
                    place.append(word.text)
                elif word.deprel == 'compound' and sentence.words[word.head-1].deprel == 'obl':
                    place.append(word.text)
                elif word.deprel == 'flat' and sentence.words[word.head-1].deprel == 'obl':
                    place.append(word.text)
        if len(place):
            dic['space'] = ' '.join(place)
        
        # find time
        for ent in sentence.ents:
            if ent.type == 'DATE':
                for i in range(len(ent.text) - 3):
                    if ent.text[i:i+4].isdigit():
                        dic['time'] = ent.text
                        break

        if 'subject' not in dic.keys(): return 0
        if 'main_verb' not in dic.keys(): return 0
        
        count = 0
        if 'object' in dic.keys(): count += 1
        if 'space' in dic.keys(): count += 1
        if 'time' in dic.keys(): count += 1
        return count


def identify(question):
    tree = question.constituency
    
    if tree.children[0].label == 'SQ':
        init_word = question.words[0]
        if init_word.upos == 'AUX':
            # binary question, not-yet-to-be-rated
            return False
        else: return None
    elif tree.children[0].label == 'SBARQ':
        init_word = question.words[0]
        if init_word.text.lower() in ['when', 'who', 'whom', 'where', 'which', 'what', 'how']:
            # wh-question, need to rate
            return True
        else: return None
    else: return None


def search_component(tree, dic):
    if tree.label != 'SQ':
        for child in tree.children:
            search_component(child, dic)
    else:
        for child in tree.children:
            if child.label == 'NP' and 'subject' not in dic:
                dic['subject'] = 1
            elif child.label == 'VP':
                for g_child in child.children:
                    if g_child.label in ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN'] and 'main_verb' not in dic:
                        dic['main_verb'] = 1
                    elif g_child.label == 'NP' and 'object' not in dic:
                        dic['object'] = 1

    return

def is_main_verb(word):
    return word.deprel == 'root' and word.upos == 'VERB' and word.xpos in ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']



for ques in doc.sentences:
    print(rating(ques))