import stanza
import aesthetic
import binary
import information as info
import rankings as rank
import os
import sys
import logging




## Init Data ##


f = open("11X11-Course-Project-Data/set1/a8.txt", "r", encoding="UTF-8")
article = f.read()
f.close()

article = article[:3000]



logger = logging.getLogger('stanza')
logger.disabled = True
nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')
logger.disabled = False

doc = nlp(article)




## Question Generators ##

def ask_when(sentence):
    word_list = ['When', 'did']

    tokens = info.get_main_info(sentence)
    if 'time' not in tokens.keys(): return None
    if 'main_verb_lemma' not in tokens.keys(): return None
    if 'main_obj' not in tokens.keys(): return None

    word_list.append(tokens['main_subj'])
    word_list.append(tokens['main_verb_lemma'])
    try:
        word_list.append(tokens['main_obj_nopp'])
    except:
        pass
    if 'location' in tokens:
        word_list.append('in')
        word_list.append(tokens['location'])



    temp = ' '.join(word_list)

    answer = " In %s." % tokens['time']

    return temp + '?' # + answer

def ask_who(sentence):
    word_list = ['Who']

    tokens = info.get_main_info(sentence)
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

    if 'time' in tokens:
        happened_time = tokens['time']
        word_list.append('in')
        word_list.append(happened_time)

    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    return temp + '?' # + ' ' + answer

def ask_where(sentence):
    word_list = ['Where']

    tokens = info.get_main_info(sentence)
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

    word_list.append(tokens['main_subj'])
    word_list.append(tokens['main_verb_lemma'])
    try:
        word_list.append(tokens['main_obj_nopp'])
    except:
        pass

    if 'time' in tokens:
        happened_time = tokens['time']
        word_list.append('in')
        word_list.append(happened_time)


    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    return temp + '?' # + ' ' + answer

def ask_what(sentence):
    word_list = ['What']

    tokens = info.get_main_info(sentence)
    if 'main_verb' not in tokens.keys(): return None
    if 'main_verb_tense' not in tokens.keys(): return None
    if 'main_obj' not in tokens.keys(): return None
    if 'main_subj' not in tokens.keys(): return None

    if tokens['main_verb_lemma'] == 'be':
        word_list.append(tokens['main_verb'])
        word_list.append(tokens['main_subj'])
        answer = tokens['main_obj']
    else:
        asking_aux = None
        if tokens['main_verb_tense'] == 'VB': asking_aux = 'do'
        elif tokens['main_verb_tense'] == 'VBD': asking_aux = 'did'
        # elif tokens['main_verb_tense'] == 'VBN':
        #     asking_aux = ''
        elif tokens['main_verb_tense'] == 'VBP': asking_aux = 'do'
        elif tokens['main_verb_tense'] == 'VBZ':
            asking_aux = 'does'
        if asking_aux == None: return None
        word_list.append(asking_aux)
        word_list.append(tokens['main_subj'])
        word_list.append(tokens['main_verb_lemma'])
        if 'location' in tokens:
            word_list.append('in')
            word_list.append(tokens['location'])

        if 'time' in tokens:
            happened_time = tokens['time']
            if 'in ' not in happened_time:
                word_list.append('in')
            word_list.append(happened_time)
    
    temp = ' '.join(word_list)
    if temp[-1] == ' ': temp = temp[:-1]

    return temp + '?'


def ask_binary(sentence):
    tree = sentence.constituency.children[0].children

    if tree[0].label != "NP" or tree[1].label != "VP": return

    verb = tree[1].children[0].children[0]
    verb = str(verb)
    if len(sentence.words) > 15: return

    ques = None
    for i, word in enumerate(sentence.words):
        if i == 0:
            continue
        prevTag = sentence.words[i - 1].upos
        if word.text == verb:
            if word.upos == "AUX" and (prevTag == "PROPN" or prevTag == "PRON" or prevTag == "NOUN"):
                ques = binary.binary_question_aux(sentence, word.text)
            elif word.feats != None:
                ques = binary.binary_question_compound(sentence, word.text)
            break
    return ques   


## Main Run ##

# g = open("questions.txt", "w")

questions_lst = []
for sentence in doc.sentences:
    sentence = nlp(sentence.text).sentences[0]
    temp_binary = ask_binary(sentence)
    temp_who = aesthetic.eliminate_space(ask_who(sentence))
    temp_when = aesthetic.eliminate_space(ask_when(sentence))
    temp_where = aesthetic.eliminate_space(ask_where(sentence))
    temp_what = aesthetic.eliminate_space(ask_what(sentence))
    if temp_binary is not None:
        questions_lst.append(temp_binary)
    if temp_who is not None:
        questions_lst.append(temp_who)
    if temp_when is not None:
        questions_lst.append(temp_when)
    if temp_where is not None:
        questions_lst.append(temp_where)
    if temp_what is not None:
        questions_lst.append(temp_what)

questions_lst_processed = []
for ques in questions_lst:
    q_doc = nlp(ques)
    r = rank.rating(q_doc)
    if r > 0:
        questions_lst_processed.append((q_doc, r))
questions_lst_processed.sort(key=lambda x:x[1])

for i in range(3):
    try:
        q = questions_lst_processed.pop()
        print('Q: ' + info.replace_pron(q[0].text, doc, nlp))
        print('Score: %d' % q[1])
    except:
        break

# g.close()

