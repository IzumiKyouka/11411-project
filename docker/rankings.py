import information as info

def rating(question):
    q_type = identify(question)
    if q_type is None:
        return 0
    elif not q_type:
        length = len(question.sentences[0].words)
        if length >= 12: return 4
        elif length >= 9: return 3
        elif length >= 6: return 2
        else: return 1
    else:
        tree = question.sentences[0].constituency
        dic = dict()
        # find subject, verb, object
        search_component(tree, dic)

        sentence = question

        # find location
        place = []
        for i in range(len(sentence.sentences[0].words)):
            word = sentence.sentences[0].words[i]
            tok = sentence.sentences[0].tokens[i]
            if ('ORG' in tok.ner) or ('GPE' in tok.ner) or ('LOC' in tok.ner):
                if word.deprel == 'obl' and info.is_main_verb(sentence.sentences[0].words[word.head - 1]):
                    place.append(word.text)
                elif word.deprel == 'compound' and sentence.sentences[0].words[word.head - 1].deprel == 'obl':
                    place.append(word.text)
                elif word.deprel == 'flat' and sentence.sentences[0].words[word.head - 1].deprel == 'obl':
                    place.append(word.text)
        if len(place):
            dic['space'] = ' '.join(place)

        # find time
        for ent in sentence.sentences[0].ents:
            if ent.type == 'DATE':
                for i in range(len(ent.text) - 3):
                    if ent.text[i:i + 4].isdigit():
                        dic['time'] = ent.text
                        break

        if 'subject' not in dic.keys(): return 0
        if 'main_verb' not in dic.keys(): return 0

        count = 0
        if 'object' in dic.keys(): count += 1
        if 'space' in dic.keys(): count += 1
        if 'time' in dic.keys(): count += 1
        if 'descript' in dic.keys(): count += 1
        if 'method' in dic.keys(): count += 1
        return count % 5


def identify(question):
    tree = question.sentences[0].constituency

    if tree.children[0].label == 'SQ':
        init_word = question.sentences[0].words[0]
        if init_word.upos == 'AUX':
            # binary question, not-yet-to-be-rated
            return False
        else:
            return None
    elif tree.children[0].label == 'SBARQ':
        init_word = question.sentences[0].words[0]
        if init_word.text.lower() in ['when', 'who', 'whom', 'where', 'which', 'what', 'how']:
            # wh-question, need to rate
            return True
        else:
            return None
    else:
        return None


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
