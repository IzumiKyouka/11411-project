import stanza
import aesthetic
import information as info


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

    tokens = info.get_main_info(sentence)
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

