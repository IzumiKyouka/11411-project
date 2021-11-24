import stanza
import aesthetic


## Init Data ##

f = open("11X11-Course-Project-Data/set1/a8.txt", "r", encoding="UTF-8")
article = f.read()
f.close()

article = article[:3000]

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')

doc = nlp(article)



## Question Generators ##

def ask_when(sentence):
    word_list = ['When', 'did']

    tokens = get_main_info(sentence)
    if 'time' not in tokens.keys(): return None
    if 'main_verb_lemma' not in tokens.keys(): return None
    if 'main_obj' not in tokens.keys(): return None

    if tokens['main_subj'] not in tokens['entities']:
        tokens['main_subj'] = tokens['main_subj'].lower()
    word_list.append(tokens['main_subj'])
    word_list.append(tokens['main_verb_lemma'])
    try:
        word_list.append(tokens['main_obj_nopp'])
    except:
        pass


    temp = ' '.join(word_list)

    answer = " In %s." % tokens['time']

    return temp + '?' # + answer

def ask_who(sentence):
    word_list = ['Who']

    tokens = get_main_info(sentence)
    if 'main_verb' not in tokens.keys(): return None
    if 'main_obj' not in tokens.keys(): return None
    if 'main_subj' not in tokens.keys(): return None

    answer = None
    subject = tokens['main_subj']
    for ent in sentence.ents:
        if ent.type == 'PERSON':
            name = ent.text
            if subject in name:
                answer = name
                break
    if answer is None: return None

    word_list.append(tokens['main_verb'])
    try:
        word_list.append(tokens['main_obj'])
    except:
        pass

    try:
        happened_time = tokens['time']
        word_list.append('in')
        word_list.append(happened_time)
    except:
        pass

    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    return temp + '?' # + ' ' + answer

def ask_where(sentence):
    word_list = ['Where']

    tokens = get_main_info(sentence)
    if 'location' not in tokens.keys(): return None
    if 'main_verb' not in tokens.keys(): return None
    if 'main_verb_tense' not in tokens.keys(): return None
    if 'main_obj' not in tokens.keys(): return None
    if 'main_subj' not in tokens.keys(): return None

    asking_aux = None
    if tokens['main_verb_tense'] == 'VB': asking_aux = 'do'
    elif tokens['main_verb_tense'] == 'VBD': asking_aux = 'did'
    # elif tokens['main_verb_tense'] == 'VBN':
    #     asking_aux = ''
    elif tokens['main_verb_tense'] == 'VBP': asking_aux = 'do'
    elif tokens['main_verb_tense'] == 'VBZ':
        asking_aux = 'does'
    
    if asking_aux is None: return None
    word_list.append(asking_aux)

    # first version: no prep
    answer = tokens['location']
    # second version: with prep (harder)

    if tokens['main_subj'] not in tokens['entities']:
        tokens['main_subj'] = tokens['main_subj'].lower()
    word_list.append(tokens['main_subj'])
    word_list.append(tokens['main_verb_lemma'])
    try:
        word_list.append(tokens['main_obj_nopp'])
    except:
        pass

    try:
        happened_time = tokens['time']
        word_list.append('in')
        word_list.append(happened_time)
    except:
        pass

    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    return temp + '?' # + ' ' + answer



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



## Helper Functions ##

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



    
## Main Run ##

g = open("questions.txt", "w")

for sentence in doc.sentences:
    temp_who = aesthetic.eliminate_space(ask_who(sentence))
    temp_when = aesthetic.eliminate_space(ask_when(sentence))
    temp_where = aesthetic.eliminate_space(ask_where(sentence))
    if temp_who is not None:
        g.write(temp_who+'\n')
    if temp_when is not None:
        g.write(temp_when+'\n')
    if temp_where is not None:
        g.write(temp_where+'\n')

g.close()

