from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import stanza

nlp = stanza.Pipeline(lang='en', processors='tokenize')

# Uses the cosine similarity of the TF-IDF to locate the top n most possible sentences that contains the answer
def locate_answer_sentence(filename, question, n):
    f = open(filename, "r", encoding="UTF-8")
    text = f.read()
    article = nlp(text)
    article_list = []
    for sentence in article.sentences:
        article_list.append(sentence.text)
    # article = article.replace(";", ".")
    # article_list = article.split(".")
    f.close()
    
    article_list.append(question)
    vect = TfidfVectorizer(min_df=1, stop_words="english", ngram_range=(1,3))
    tfidf = vect.fit_transform(article_list)
    pairwise_similarity = tfidf * tfidf.T
       
    question_similarity = pairwise_similarity[-1].toarray()[0]
    question_similarity[-1] = -10000
    res = []
    for i in range(n):
        answer_index = np.argmax(question_similarity)
        res.append(article_list[answer_index])
        question_similarity[answer_index] = -10000
    
    return res


