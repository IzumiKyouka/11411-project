import stanza
import information as info
import locate_answer_sentence as locate

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse,constituency,ner')


def answer_when(closest):
    tokens = info.get_main_info(closest)
    try:
        return " In %s." % tokens['time']
    except:
        return None

def answer_where(closest):
    tokens = info.get_main_info(closest)
    try:
        return ' ' + tokens['location']
    except:
        return None

def answer_who_whom(closest):
    pass

def answer_what(closest):
    pass

def answer_which(closest):
    pass

def answer_how(closest):
    pass




## Determine Question Types ##

def classify(ques):
    for word in ques.words:
        if word.text.lower() in ['who', 'whom', 'when', 'where', 'what', 'which', 'how']:
            return word.text.lower()
    return 'binary'



## Main run ##

questions = "When did Ronaldo score his 500th senior career goal for club and country? Where was Ronaldo born?"
question_sentences = nlp(questions).sentences

for question in question_sentences:
    question_text = question.text
    sentence = locate.locate_answer_sentence("11X11-Course-Project-Data/set1/a8.txt", question_text)
    closest_sentence = nlp(sentence).sentences[0]

    question_type = classify(question)
    if question_type == 'when':
        print(answer_when(closest_sentence))
    elif question_type == 'where':
        print(answer_where(closest_sentence))
    elif question_type in ['who', 'whom']:
        print(answer_who_whom(closest_sentence))
    elif question_type == 'what':
        print(answer_what(closest_sentence))
    elif question_type == 'which':
        print(answer_which(closest_sentence))
    elif question_type == 'how':
        print(answer_how(closest_sentence))
    elif question_type == 'binary':
        pass




