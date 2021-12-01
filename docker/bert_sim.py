import numpy as np
from scipy import spatial
from sent2vec.vectorizer import Vectorizer


def locate_answer_sentence_w_bert(article_list, question, n):    
    vectorizer = Vectorizer()
    article_list.append(question.text)
    vectorizer.bert(article_list)
    vectors_bert = vectorizer.vectors

    similarities = np.array([spatial.distance.cosine(vectors_bert[i], vectors_bert[-1]) 
                            for i in range(len(article_list))])
    sentence_list = []
    for i in range(n):
        answer_index = np.argmax(similarities)
        sentence_list.append(article_list[answer_index])
        similarities[answer_index] = -10000
    
    article_list = article_list[:-1]
    return sentence_list
