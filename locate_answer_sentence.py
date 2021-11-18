from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Uses the cosine similarity of the TF-IDF to locate the sentence that contains the answer
def locate_answer_sentence(filename, question):
    f = open(filename, "r", encoding="UTF-8")
    article = f.read()
    article = article.replace(";", ".")
    article_list = article.split(".")
    f.close()
    
    article_list.append(question)
    vect = TfidfVectorizer(min_df=1, stop_words="english", ngram_range=(1,3))
    tfidf = vect.fit_transform(article_list)
    pairwise_similarity = tfidf * tfidf.T
       
    question_similarity = pairwise_similarity[-1].toarray()[0]
    question_similarity[-1] = 0
    answer_index = np.argmax(question_similarity)
    return article_list[answer_index]

