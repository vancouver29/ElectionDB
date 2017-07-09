#!/usr/bin/python
import psycopg2
from config import db_config
import re
import csv

def word_count(tweets):
    counts = dict()
    for tweet in tweets:
        tweet = tweet.lower()
        # remove links & tags & mentions
        tweet = re.sub('https?\S+', '', tweet)
        tweet = re.sub('#\w+', '', tweet)
        tweet = re.sub('@\w+', '', tweet)
        # extract all words
        words = re.findall('\w+', tweet)
        # for each word, update count in dict
        for word in words:
            if counts.has_key(word):
                counts[word] += 1
            else:
                counts[word] = 1

    return counts


# MAIN
# -----------------------------------------------------------------------

if __name__ == '__main__':

    conn = None

    try:
        print "connecting to DB..."
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        print "connected!"

        # get all tweets
        cur.execute("SELECT content FROM Tweets;")
        tweets = map(lambda x: x[0], cur.fetchall())

        word_count = word_count(tweets).items()
        word_count.sort(key=lambda x: x[1])
        word_count.reverse()

        f = open('word_counts.csv', 'wb')
        writer = csv.writer(f)

        for word, count in word_count:
            writer.writerow((word, str(count)))




    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        f.close()
        if conn is not None:
            conn.close()
