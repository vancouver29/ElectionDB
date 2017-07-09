#!/usr/bin/python
from copy import deepcopy
import random
from vectors import *

class Cluster():

    def __init__(self, centroid, documents):
        self.centroid = centroid    # a doc vector
        self.documents = documents  # set of docs

    def calculate_center(self):
        # get list of doc vectors
        vectors = map(lambda x: x.vector, self.documents)
        # num of vectors
        n = len(vectors)
        # zip all vectors together (makes column tuples)
        vector = zip(*vectors)
        # take the average of the tuples
        vector = map(lambda x: sum(x)/float(n), vector)
        # this is new centroid
        self.centroid = vector


def closest_cluster(v, clusters):
    # initially, first cluster is closest
    closest = clusters[0]
    # check remaining for closest
    for c in clusters[1:]:
        # if similarity between v and c's center is higher
        if cosine_similarity(v, c.centroid) > cosine_similarity(v, closest.centroid):
            # its new closest
            closest = c

    return closest

def cosine_similarity(v1, v2):
    return dot_product(v1, v2)/float(magnitude(v1) * magnitude(v2))

def dot_product(v1, v2):
    return sum([x * y for x, y in zip(v1,v2)])

def magnitude(v):
    return pow(sum(map(lambda x: pow(x,2), v)), 0.5)

def k_means(k, documents):

    done = False
    prev_clusters = None
    clusters = list()

    # get k random docs, set as centroids for new clusters
    for doc in random.sample(documents, k):
        clusters.append(Cluster(doc.vector, set()))

    iteration = 0
    while not done:
        iteration += 1
        print 'iteration:', iteration

        # for each foc
        for doc in documents:
            # put in closest cluster
            closest = closest_cluster(doc.vector, clusters)
            closest.documents.add(doc)

        # check exit condition
        if prev_clusters is not None:
            # for each cluster
            for i in range(k):
                # if exists a difference
                if prev_clusters[i].documents != clusters[i].documents:
                    done = False
                    break
            else:
                done = True

        # make copy
        prev_clusters = deepcopy(clusters)

        for cluster in clusters:
            # recompute centroid & clear records set
            cluster.calculate_center()
            cluster.documents.clear()

    return prev_clusters


if __name__ == '__main__':
    print 'getting docs...'
    documents = get_vectors()
    print 'calculating clusters...'
    clusters = k_means(10, set(documents))
    print 'done!'

    for i in range(len(clusters)):
        print ''
        print '----------------------------'
        print ''
        print 'CLUSTER', i + 1
        for tag in clusters[i].documents:
            print tag.name
