import stanza

f = open("11X11-Course-Project-Data/set1/a8.txt", "r", encoding="UTF-8")
article = f.read()
f.close()

article = article[:10000]

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')

doc = nlp(article)




# this function assumes the given sentence contains a time phrase
def ask_when(sentence):
    word_list = ['When', 'did']

    tokens = get_main_info(sentence)
    if 'year' not in tokens.keys(): return None
    if 'main_verb_lemma' not in tokens.keys(): return None
    if 'main_obj' not in tokens.keys(): return None

    word_list.append(tokens['main_subj'])
    word_list.append(tokens['main_verb_lemma'])
    try:
        word_list.append(tokens['main_obj'])
    except:
        pass

    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    try:
        month = tokens['month'] + ' '
    except:
        month = ''
    try:
        year = tokens['year']
    except:
        year = ''
    answer = " In %s%d." % (month, year)

    return temp + '?' + answer

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
        month = tokens['month'] + ' '
    except:
        month = ''
    try:
        year = tokens['year']
    except:
        year = None
    if year is not None:
        happened_time = "in %s%d" % (month, year)
    else:
        happened_time = ''
    
    word_list.append(happened_time)

    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    return temp + '?' + ' ' + answer


def find_head(word):
    return word.head

def find_root(sentence):
    for word in sentence.words:
        if word.deprel == 'root': return word

def is_main_verb(word):
    return word.deprel == 'root' and word.upos == 'VERB' and word.xpos in ['VB', 'VBP', 'VBZ', 'VBD', 'VBG', 'VBN']

def is_month(word):
    month_set = {'January', 'February', 'March', 'April', 
                 'May', 'June', 'July', 'August', 
                 'September', 'October', 'November', 'December'}
    return word.text in month_set

def is_const_word(part):
    return len(part.children) == 0

def add_to_list(lst, child):
    if not is_const_word(child):
        for g_child in child.children:
            add_to_list(lst, g_child)
    else:
        text = child.label
        lst.append(text)

def get_main_info(sentence):
    return_tokens = dict()

    for word in sentence.words:
        # identify action
        if is_main_verb(word):
            return_tokens['main_verb'] = word.text
            return_tokens['main_verb_lemma'] = word.lemma

        # identify time
        if word.upos == 'NUM' and word.text.isdigit() and len(word.text) == 4:
            return_tokens['year'] = int(word.text)
            check_month = sentence.words[word.head - 1]
            if is_month(check_month) and is_main_verb(sentence.words[check_month.head - 1]):
                return_tokens['month'] = check_month.text

    
    for child in sentence.constituency.children[0].children:
        if child.label == 'NP':
            subj_list = []
            add_to_list(subj_list, child)
            subject = ' '.join(subj_list)
            return_tokens['main_subj'] = subject
        if child.label == 'VP':
            obj_list = []
            for g_child in child.children:
                if g_child.label == 'VBD':
                    verb = g_child.children[0].label
                    return_tokens['main_verb'] = verb
                elif g_child.label == 'NP':
                    add_to_list(obj_list, g_child)
                    object = ' '.join(obj_list)
                    return_tokens['main_obj'] = object
    
    return return_tokens


for sentence in doc.sentences:
    temp = ask_who(sentence)
    if temp is not None:
        print()
        print(temp)

    
    

