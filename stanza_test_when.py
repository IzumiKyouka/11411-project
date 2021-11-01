import stanza

f = open("11X11-Course-Project-Data/set1/a8.txt", "r", encoding="UTF-8")
article = f.read()
f.close()

article = article[:20000]

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency')

doc = nlp(article)

def run():
    for sentence in doc.sentences:
        for word in sentence.words:
            if word.deprel == 'root':
                # print("the root word %s has POS tag upos:%s, xpos:%s" % (word.text, word.upos, word.xpos))
                root_word = word
                root_postag = word.upos
        if root_postag == 'VERB':
            for word in sentence.words:
                if word.head == root_word.id and word.deprel == 'nsubj':
                    subj_word = word
                if word.upos == 'NUM' and len(word.text) == 4 and word.head == root_word.id:
                    year = int(word.text)
        try:
            if root_word.xpos == 'VBD':
                try:
                    verb = root_word.lemma
                    something = ["%s" % verb]
                    for word in sentence.words[root_word.id:]:
                        if word.xpos not in ['PRP$', 'JJ', 'NN', 'IN', 'CC', 'DT', 'NNP']: break
                        something.append(word.text)
                    mid = ' '.join(something)
                    question = ("When did %s " % subj_word.text) + mid + "?"
                    answer = "In %d" % year
                    print()
                    print(question)
                    print(answer)
                except:
                    pass
        except:
            pass


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
        # # identify action
        if is_main_verb(word):
            return_tokens['main_verb_lemma'] = word.lemma
        # if word.deprel == 'aux' and is_main_verb(sentence.words[word.head - 1]):
        #     return_tokens['aux_verb'] = word
        # if word.lemma == 'not':
        #     return_tokens['negation'] = True
        
        # # identify agent
        # if word.deprel == 'nsubj' and is_main_verb(sentence.words[word.head - 1]):
        #     subject_word = word.text

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
            # verb_list = []
            obj_list = []
            for g_child in child.children:
                if g_child.label == 'VBD':
                    # add_to_list(verb_list, g_child)
                    verb = g_child.children[0].label
                    return_tokens['main_verb'] = verb
                elif g_child.label == 'NP':
                    add_to_list(obj_list, g_child)
                    object = ' '.join(obj_list)
                    return_tokens['main_obj'] = object
    
    return return_tokens


for sentence in doc.sentences:
    temp = ask_when(sentence)
    if temp is not None:
        print()
        print(ask_when(sentence))

    
    

