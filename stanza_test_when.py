import stanza

article = """Cristiano Ronaldo dos Santos Aveiro GOIH (born 5 February 1985), known as Cristiano Ronaldo, is a Portuguese professional footballer who plays for Spanish club Real Madrid and the Portugal national team. He is a forward and serves as captain for Portugal. By the age of 22, Ronaldo had received Ballon d'Or and FIFA World Player of the Year nominations. The following year, in 2008, he won his first Ballon d'Or and FIFA World Player of the Year awards. He then won the FIFA Ballon d'Or in 2013 and 2014. In September 2015, Ronaldo scored his 500th senior career goal for club and country.
Often ranked as the best player in the world and rated by some in the sport as the greatest of all time, in 2015 Ronaldo was named the best Portuguese player of all time by the Portuguese Football Federation, during its 100th anniversary celebrations. He is the first player to win four European Golden Shoe awards. With Manchester United and Real Madrid, Ronaldo has won three Premier Leagues, one La Liga, one FA Cup, two Football League Cups, two Copas del Rey, two UEFA Champions Leagues, one UEFA Super Cup and two FIFA Club World Cups."""

nlp = stanza.Pipeline(lang='en', processors='tokenize,mwt,pos,lemma,depparse')

doc = nlp(article)

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

print()