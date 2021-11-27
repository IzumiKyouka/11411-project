from nltk.corpus import wordnet
## Information Seeker ##

def get_main_info(sentence):
    return_tokens = dict()

    # identify time
    for ent in sentence.ents:
        if ent.type == 'DATE':
            for i in range(len(ent.text) - 3):
                if ent.text[i:i+4].isdigit():
                    return_tokens['time'] = ent.text
                    break
    entities = [ent.text for ent in sentence.ents]
    return_tokens['entities'] = entities
    # print(entities)

    # identify action
    for word in sentence.words:
        if is_main_verb(word):
            return_tokens['main_verb'] = word.text
            return_tokens['main_verb_lemma'] = word.lemma
            return_tokens['main_verb_tense'] = word.xpos
    
    # identify location
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
        return_tokens['location'] = ' '.join(place)
    
    for child in sentence.constituency.children[0].children:
        # identify agent
        if child.label == 'NP':
            subj_list = []
            add_to_list_all(subj_list, child, entities, True)
            subject = ' '.join(subj_list)
            return_tokens['main_subj'] = subject
        # identify event
        if child.label == 'VP':
            obj_list = []
            obj_list_nopp = []
            for g_child in child.children:
                if g_child.label == 'VBD':
                    verb = g_child.children[0].label
                    # return_tokens['main_verb'] = verb
                elif g_child.label == 'NP':
                    add_to_list_all(obj_list, g_child)
                    add_to_list_without_pp(obj_list_nopp, g_child)
                    object = ' '.join(obj_list)
                    object_nopp = ' '.join(obj_list_nopp)
                    return_tokens['main_obj'] = object
                    return_tokens['main_obj_nopp'] = object_nopp
    
    return return_tokens

def compare_binary(question, sentence):
    must_include = ["NOUN", "ADJ", "VERB", "PROPN", "NUM"]
    negations = ["no", "not", "none", "never", "cannot"]
    res = 0
    for word in question.words:
        if word.lemma in negations:
            res += 1
        if word.upos in must_include:
            tmp = exists(word.lemma, sentence)
            if  tmp == -1:
                return False
            res += tmp
    for word in sentence.words:
        if word.lemma in negations:
            res += 1
    return res % 2 == 0


## Helper Functions ##

def exists(word, sentence):
    synonyms = []
    antonyms = []
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
            if l.antonyms():
                antonyms.append(l.antonyms()[0].name())
    synonyms = set(synonyms)
    antonyms = set(antonyms)
    # print(word, synonyms)
    # print(word, antonyms)
    for sent_word in sentence.words:
        word_lemma = sent_word.lemma
        if word_lemma == word or word_lemma in synonyms:
            return 0
        if word_lemma in antonyms:
            return 1
    return -1
        

def find_head(word):
    return word.head

def find_root(sentence):
    for word in sentence.words:
        if word.deprel == 'root': return word

def is_main_verb(word):
    return word.deprel == 'root' and word.upos == 'VERB' and word.xpos in ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']

def is_const_word(part):
    return len(part.children) == 0

def add_to_list_all(lst, child, entity=[], subject=False):
    if not is_const_word(child):
        for g_child in child.children:
            add_to_list_all(lst, g_child)
    else:
        text = child.label
        if not subject:
            lst.append(text)
        else:
            if text in entity:
                lst.append(text)
            else:
                lst.append(text.lower())
                print(text, text.lower())

def add_to_list_without_pp(lst, child):
    if not is_const_word(child):
        for g_child in child.children:
            if g_child.label == 'PP':
                continue
            add_to_list_all(lst, g_child)
    else:
        text = child.label
        lst.append(text)
