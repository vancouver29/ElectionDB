#!/usr/bin/python
import psycopg2
from config import db_config
import json

# return list of distinct hashtags.
#
def listOfHashtags():

    conn = None
    tags = None

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # get all hashtags & unpack the tuples
        cur.execute("SELECT DISTINCT tag FROM Hashtags")
        tags = map(lambda x: x[0], cur.fetchall())

    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        if conn is not None:
            conn.close()

    return tags


# return list hashtag pairs (tuples) where the pairs occur
# together at least once.
#
def listOfPairs():

    conn = None
    pairs = None

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # selects all unique pairwise occurrences, where (a, b) == (b, a)
        sql =   """
                SELECT      A.tag, B.tag
                FROM        Hashtags AS A, Hashtags AS B
                WHERE       A.tweet_handle = B.tweet_handle AND
                            A.tweet_time = B.tweet_time AND
                            A.tag > B.tag
                GROUP BY    (A.tag, B.tag)
                ORDER BY COUNT(*) DESC
                """

        # get all pairs
        cur.execute(sql)
        pairs = cur.fetchall()

    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        if conn is not None:
            conn.close()

    return pairs


# generate JSON file describing a graph of hashtags (nodes), where
# two nodes are connected iff they occur together at least once.
#
def generateJSONNetworkGraph():
    # array of hashtags (strings)
    tags = listOfHashtags()
    # array of tuples ('tagA', 'tagB')
    pairs = listOfPairs()
    # convert to dictionary with tag as key, hashtag as value
    nodes = map(lambda x: { 'tag': x }, tags)
    # conver to dictionary, with source & target as keys, tagA & tagB as values
    edges = map(lambda x: { 'source': x[0], 'target': x[1] }, pairs)

    # give each node dict a unique id
    for i, node in enumerate(nodes):
        node['id'] = i

    # give each edge dict a unique id
    for i, edge in enumerate(edges):
        edge['id'] = i

    # create json file
    with open('hashtagNetwork.json', 'w') as outfile:
        # the data to write into json
        data = { 'nodes': nodes, 'edges': edges }
        # convert data to json format
        s = json.dumps(data, indent=4, separators=(',',':'), sort_keys=True)
        # write to the file
        outfile.write(s)


if __name__ == '__main__':
    generateJSONNetworkGraph()
