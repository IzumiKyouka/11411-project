from nltk.corpus import wordnet
import nltk
import stanza
import aesthetic
import information as info
import locate_answer_sentence as locate

## Information Seeker ##

# nltk.download('wordnet')


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
        if is_main_verb(word) or is_aux_verb(word):
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
            add_to_list_all(subj_list, child, entities)
            subject = ' '.join(subj_list)
            return_tokens['main_subj'] = subject
        # identify event
        if child.label == 'VP':
            obj_list = []
            obj_list_nopp = []
            descriptive_list = []
            method_list = []
            for g_child in child.children:
                if g_child.label in ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']:
                    verb = g_child.children[0].label
                    if 'main_verb' not in return_tokens:
                        return_tokens['main_verb'] = verb
                elif g_child.label == 'NP':
                    add_to_list_all(obj_list, g_child, entities)
                    add_to_list_without_pp(obj_list_nopp, g_child, entities)
                    object = ' '.join(obj_list)
                    object_nopp = ' '.join(obj_list_nopp)
                    return_tokens['main_obj'] = object
                    return_tokens['main_obj_nopp'] = object_nopp
                elif g_child.label in ['ADJP', 'ADVP']:
                    add_to_list_all(descriptive_list, g_child, entities)
                    descriptive = ' '.join(descriptive_list)
                    return_tokens['descript'] = descriptive
                elif g_child.label == 'PP' and 'time' not in return_tokens and 'location' not in return_tokens:
                    add_to_list_all(method_list, g_child, entities)
                    methods = ' '.join(method_list)
                    return_tokens['method'] = methods

    
    return return_tokens

def get_main_info_ques(dic, tree):
    if tree.label in ['WHADJP', 'WHAVP', 'WHNP', 'WHPP']:
        dic['type'] = tree.label
    elif tree.label == 'SQ':
        for child in tree.children:
            if child.label == 'VP':
                for g_child in child.children:
                    if g_child.label in ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN'] and 'ask_verb' not in dic:
                        dic['ask_verb'] = g_child.children[0].label
                    elif g_child.label == 'NP' and 'main_object' not in dic:
                        lst1 = []
                        add_to_list_all(lst1, g_child)
                        dic['main_object'] = ' '.join(lst1)
                    elif g_child.label == 'VP':
                        lst2 = []
                        add_to_list_all(lst2, g_child)
                        dic['verb_cont'] = ' '.join(lst2)
    else:
        for child in tree.children:
            get_main_info_ques(dic, child)

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

def is_aux_verb(word):
    return word.deprel == 'cop' and word.upos == 'AUX'

def is_const_word(part):
    return len(part.children) == 0

def add_to_list_all(lst, child, entity=[]):
    if not is_const_word(child):
        for g_child in child.children:
            add_to_list_all(lst, g_child, entity)
    else:
        text = child.label
        if text not in entity:
            lst.append(text.lower())
        else:
            lst.append(text)

def add_to_list_without_pp(lst, child, entity=[]):
    if not is_const_word(child):
        for g_child in child.children:
            if g_child.label == 'PP':
                continue
            add_to_list_all(lst, g_child, entity)
    else:
        text = child.label
        if text not in entity:
            lst.append(text.lower())
        else:
            lst.append(text)

def is_pron(text):
    text = text.lower()
    lst = ['I', 'me', 'my', 'mine',
           'you', 'your', 'your', 
           'he', 'him', 'his', 
           'she', 'her', 'hers',
           'it', 'its',
           'they', 'them', 'their', 'theirs']
    return text in lst


def replace_pron(sent, doc, nlp):
    s = nlp(sent).sentences[0]
    ne = doc.ents[0].text

    for word in s.words:
        if word.xpos == "PRP":
            sent = sent.replace(" "+ word.text + " ", " " + ne + " ")
            break
        if word.xpos == "PRP$":
            sent = sent.replace(" "+ word.text + " ", " " + ne + "'s ")
            break
    
    return sent
            
        