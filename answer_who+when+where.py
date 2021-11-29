import stanza
import aesthetic
import information as info
import locate_answer_sentence as locate

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')


def answer_when(closest):
    tokens = info.get_main_info(closest)
    try:
        return "In %s." % tokens['time']
    except:
        return None

def answer_where(closest):
    tokens = info.get_main_info(closest)
    try:
        return tokens['location']
    except:
        return None


def answer_who_whom(question, sentence):
    answer_doc = nlp(sentence)
    question_doc = nlp(question)
    candi = list()

    # if answer sentence only has one ent with type "PERSON", return that as answer
    for ent in answer_doc.ents:
        if ent.type == "PERSON":
            candi.append(ent)
    if len(candi) == 1:
        print(candi[0])
        return candi[0].text

    # if there are more than 1 ent, we decide by matching the relation between the verb and the subject between Q and A
    target = None
    if len(candi) > 1:
        for sent in question_doc.sentences:
            for word in sent.words:
                if word.deprel == "nsubj":
                    target = "nsubj"
                if word.deprel == "nsubj:pass":
                    target = "nsubj:pass"
        if target is not None:
            for sent in answer_doc.sentences:
                for word in sent.words:
                    if word.deprel == target:
                        for c in candi:
                            if str(word) == c.text:
                                return str(word)

    # if this still doesn't work, we just use the dependency parsing to find an answer.
    for sent in answer_doc.sentences:
        for word in sent.words:
            if word.deprel == target:
                return str(word)


def answer_what_which(closest, question):
    tree = question.constituency
    qtokens = dict()
    info.get_main_info_ques(qtokens, tree)
    if 'ask_verb' not in qtokens: return

    atokens = info.get_main_info(closest)
    
    # identify asking verb
    if qtokens['ask_verb'] in ['am', 'are', 'is', 'was', 'were']:
        try:
            return atokens['main_subj']
        except:
            return None
    else:
        try:
            return atokens['main_obj']
        except:
            return None

def answer_which(closest):
    pass

def answer_how(closest):
    pass

def answer_binary(ques, sent):
    for s in sent:
        c = nlp(s).sentences[0]
        res = info.compare_binary(ques, c)
        if res:
            return "Yes."
    return "No."




## Determine Question Types ##

def classify(ques):
    for word in ques.words:
        if word.text.lower() in ['who', 'whom', 'when', 'where', 'what', 'which', 'how']:
            return word.text.lower()
    return 'binary'



## Main run ##

questions = "When did Ronaldo score his 500th senior career goal for club and country? Where was Ronaldo born? What did Ronaldo score in September 2015?"
question_sentences = nlp(questions).sentences

for question in question_sentences:
    question_text = question.text
    sentences = locate.locate_answer_sentence("11X11-Course-Project-Data/set1/a8.txt", question_text, 3)

    for sentence in sentences:
        closest_sentence = nlp(sentence).sentences[0]

        question_type = classify(question)
        answer = None
        if question_type == 'when':
            answer = answer_when(closest_sentence)
        elif question_type == 'where':
            answer = answer_where(closest_sentence)
        elif question_type in ['who', 'whom']:
            answer = answer_who_whom(question, closest_sentence)
        elif question_type in ['what', 'which', 'whose']:
            answer = answer_what_which(closest_sentence, question)
        elif question_type == 'how':
            answer = answer_how(closest_sentence)
        elif question_type == 'binary':
            answer = answer_binary(question, sentence)
        
        if answer is not None:
            print(aesthetic.capitalize_init(answer))
            break





