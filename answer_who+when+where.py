import stanza
import aesthetic
import information as info
import locate_answer_sentence as locate

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')


def answer_when(closest):
    """
    Parameters
    ----------
    closest : str
        The sentence that is closest to the input question.

    Return
    ----------
    str
        Answer to the question.
    """
    closest_stanza = nlp(closest).sentences[0]
    tokens = info.get_main_info(closest_stanza)
    try:
        return "In %s." % tokens['time']
    except:
        return None

def answer_where(closest):
    """
    Parameters
    ----------
    closest : str
        The sentence that is closest to the input question.

    Return
    ----------
    str
        Answer to the question.
    """
    closest_stanza = nlp(closest).sentences[0]
    tokens = info.get_main_info(closest_stanza)
    try:
        return tokens['location']
    except:
        return None


def answer_who_whom(question, sentence):
    """
    Parameters
    ----------
    question : str
        The input question
    sentence : str
        The sentence that is closest to the question

    Return
    ----------
    str
        Answer to the question.
    """
    answer_doc = nlp(sentence)
    question_doc = nlp(question)
    candi = list()

    # if answer sentence only has one ent with type "PERSON", return that as answer
    for ent in answer_doc.ents:
        if ent.type == "PERSON":
            candi.append(ent)
    if len(candi) == 1:
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
    """
    Parameters
    ----------
    closest : str
        The sentence that is closest to the question
    question : str
        The input question

    Return
    ----------
    str
        Answer to the question.
    """
    closest_stanza = nlp(closest).sentences[0]
    question_stanza = nlp(question).sentences[0]
    tree = question_stanza.constituency
    qtokens = dict()
    info.get_main_info_ques(qtokens, tree)
    if 'ask_verb' not in qtokens: return

    atokens = info.get_main_info(closest_stanza)
    
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

def answer_binary(question, sentences):
    for s in sentences:
        res = info.compare_binary(question, s)
        if res:
            return "Yes."
    return "No."




## Determine Question Types ##

def classify(question):
    question_stanza = nlp(question).sentences[0]
    for word in question_stanza.words:
        if word.text.lower() in ['who', 'whom', 'when', 'where', 'what', 'which', 'how']:
            return word.text.lower()
    return 'binary'



## Main run ##

question = "Did Ronaldo receive the PFA Players' Player of the Year award?"
question_type = classify(question)
answer = None

sentences = locate.locate_answer_sentence("11X11-Course-Project-Data/set1/a8.txt", question, 3)

for sentence in sentences:
    if question_type == 'when':
        answer = answer_when(sentence)
    elif question_type == 'where':
        answer = answer_where(sentence)
    elif question_type in ['who', 'whom']:
        answer = answer_who_whom(question, sentence)
    elif question_type in ['what', 'which', 'whose']:
        answer = answer_what_which(sentence, question)
    elif question_type == 'how':
        answer = answer_how(sentence)
    elif question_type == 'binary':
        answer = answer_binary(question, sentences)
    if answer is not None:
        print(aesthetic.capitalize_init(answer))
        break





