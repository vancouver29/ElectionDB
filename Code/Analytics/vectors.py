#!/usr/bin/python
import psycopg2
from config import db_config
from copy import deepcopy
import csv
import re
from math import log

# given a list of tweets (strings), returns a dict with each
# word as a key, and the count for that word.
#
def word_count(tweets):
    counts = dict()

    document = " ".join(tweets)
    document = document.lower()
    # remove links & tags & mentions
    document = re.sub('https?\S+', '', document)
    document = re.sub('#\w+', '', document)
    document = re.sub('@\w+', '', document)
    # extract all words
    words = re.findall('\w+', document)
    num_words = len(words)
    # for each word, update count in dict
    for word in words:
        if counts.has_key(word):
            counts[word] += 1
        else:
            counts[word] = 1

    # normalize
    for word, count in counts.items():
        counts[word] = count / float(num_words)

    return counts


def num_associated_docs(term, documents):
    count = 0
    for doc in documents:
        if doc.TF.has_key(term):
            count += 1
    return count

def inverse_document_freq(term, documents):
    # count how many documents the term occurs in
    count = 0
    # a doc is a Hashtag object
    for doc in documents:
        if doc.TF.has_key(term):
            count += 1

    # calculate IDF (1 + ln(num docs/count))
    if count > 0:
        return 1.0 + log(len(documents)/float(count))
    else:
        return 1.0


class Document():
    # class variable
    vector_index = None

    def __init__(self, name, TF):
        self.name = name
        self.TF = TF
        self.vector = list()

    def build_vector(self):
        # zero vector
        self.vector = [0] * len(Document.vector_index)
        # for each term in TF
        for term, count in self.TF.items():
            # set count at index for term
            self.vector[Document.vector_index[term]] = count

    def cosine_similarity(self, other_doc):
        pass

    def print_short_vector(self):
        for term, i in Document.vector_index.items():
            if self.vector[i] != 0:
                print term, self.vector[i]

    def __key(self):
        return self.name

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())


# return list of all terms found in sample space
#
def get_all_terms():

    conn = None
    words = None

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # get all tweets
        cur.execute("SELECT content FROM Tweets;")
        tweets = map(lambda x: x[0], cur.fetchall())

        # list of all terms
        words = word_count(tweets).keys()
        words.sort()

    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        if conn is not None:
            conn.close()

    return words


# return list of all distinct hashtags
#
def get_all_hashtags():

    conn = None
    tags = None

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # get all hashtags
        cur.execute("SELECT DISTINCT tag FROM Hashtags")
        tags = map(lambda x: x[0], cur.fetchall())

    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        if conn is not None:
            conn.close()

    return tags


# return document for given hashtag
#
def get_document_for_tag(tag):

    conn = None
    document = None

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # get all tweets with this tag
        sql =   """
                SELECT  content
                FROM    Hashtags, Tweets
                WHERE   tweet_handle = handle AND
                        tweet_time = time AND
                        tag = %s
                """

        cur.execute(sql, (tag,))

        # list of all tweets that contain this hashtag
        tweets = map(lambda x: x[0], cur.fetchall())
        # get TF for this tag
        TF = word_count(tweets)
        # create the term vector
        document = Document(tag, TF)

    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        if conn is not None:
            conn.close()

    return document


def trim_terms(terms, documents):
    # we still need to construct the vectors for each document,
    # to minimize dimensions, we only need to consider terms that
    # associate to at least one document.
    to_delete = list()
    # for each term in whole sample space
    for term in terms:
        # count how many documents term appears in
        count = num_associated_docs(term, documents)
        # if appears in no documents, we will remove it from the index
        if count == 0:
            to_delete.append(term)

    # delete unnecessary terms
    for term in to_delete:
        terms.remove(term)

    return terms



def get_vectors():
    # all terms in whole sample space
    terms = get_all_terms()
    # list all distinct hashtags
    hashtags = get_all_hashtags()

    # a document represents the collection of tweets that contain a
    # specific tag, together with its TF and vector
    documents = list()

    for tag in hashtags:
        doc = get_document_for_tag(tag)
        if doc is None:
            raise Exception("ERROR")
        else:
            documents.append(doc)

    # remove unnecessary terms (those that are not associated
    # with any hashtags)
    terms = trim_terms(terms, documents)

    # build the vector index
    vector_index = dict()

    for i, term in enumerate(terms):
        vector_index[term] = i


    # set the class variable
    Document.vector_index = vector_index

    # now build the vectors
    for doc in documents:
        doc.build_vector()

    # construct IDF
    IDF = dict()

    for term in terms:
        IDF[term] = inverse_document_freq(term, documents)

    # now we can weigh the vectors
    #
    for doc in documents:
        # for each term
        for term, i in vector_index.items():
            # multiply normalized TF with IDF
            doc.vector[i] *= IDF[term]



    # return all the documents
    return documents
