# Ubuntu Linux as the base image
FROM ubuntu:18.04

# Set UTF-8 encoding
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# Install Python
RUN apt-get -y update && \
    apt-get -y upgrade && \
	apt-get -y install python3-pip python3-dev

# Install spaCy
RUN pip3 install --upgrade pip
RUN pip3 install --pre stanza
RUN pip3 install sklearn
RUN pip3 install numpy
RUN pip3 install scipy
RUN pip3 install sent2vec
RUN pip3 install nltk

#RUN python3 -m stanza.download('en')

# Add the files into container, under QA folder, modify this based on your need
RUN mkdir /QA
ADD ask /QA
ADD answer /QA
ADD setup.py /QA
ADD aesthetic.py /QA
ADD bert_sim.py /QA
ADD binary.py /QA
ADD information.py /QA
ADD locate_answer_sentence.py /QA
ADD rankings.py /QA

RUN python3 QA/setup.py


# Change the permissions of programs
CMD ["chmod 777 /QA/*"]

# Set working dir as /QA
WORKDIR /QA
ENTRYPOINT ["/bin/bash", "-c"]
