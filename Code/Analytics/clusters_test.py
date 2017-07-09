#!/usr/bin/python
from copy import deepcopy
import random

class Record():

    def __init__(self, rid, age, service):
        self.rid = rid
        self.age = age
        self.service = service

    def distance_from(self, another_record):
        x = pow(abs(self.age - another_record.age), 2)
        y = pow(abs(self.service - another_record.service), 2)
        return pow(x + y, 0.5)

    def closest_cluster(self, clusters):

        closest = clusters[0]
        for cluster in clusters[1:]:
            if self.distance_from(cluster.centroid) < self.distance_from(closest.centroid):
                closest = cluster
        return closest

    def __key(self):
        return (self.rid, self.age, self.service)

    def __eq__(self, other):
        return self.__key() == other.__key()

    def __hash__(self):
        return hash(self.__key())

class Cluster():

    def __init__(self, centroid, records):
        self.centroid = centroid    # record object
        self.records = records      # set of records

    def calculate_center(self):
        # convert set of records to list of each records fields (in tuples)
        fields = map(lambda x: (x.age, x.service), self.records)
        # unzip tuples into two lists
        split = zip(*fields)
        # compute average of each field & store in centroid
        split = map(lambda x: sum(x)/float(len(self.records)), split)
        self.centroid = Record(0, split[0], split[1])



def k_means(k, records):

    done = False
    prev_clusters = None
    clusters = list()

    # init k random clusters
    for record in random.sample(records, k):
        clusters.append(Cluster(record, set()))

    while not done:
        # for each record
        for record in records:
            # put in closest cluster
            closest = record.closest_cluster(clusters)
            closest.records.add(record)

        # check exit condition
        if prev_clusters is not None:
            # for each cluster
            for i in range(k):
                # if exists a difference
                if prev_clusters[i].records != clusters[i].records:
                    print 'repeat'
                    done = False
                    break
            else:
                done = True

        # make copy
        prev_clusters = deepcopy(clusters)

        for cluster in clusters:
            # recompute centroid & clear records set
            cluster.calculate_center()
            cluster.records.clear()

    return prev_clusters


if __name__ == '__main__':

    # data
    a = Record(1, 30, 5)
    b = Record(2, 50, 25)
    c = Record(3, 50, 15)
    d = Record(4, 25, 5)
    e = Record(5, 30, 10)
    f = Record(6, 55, 25)

    clusters = k_means(2, {a,b,c,d,e,f})

    c1 = map(lambda x: x.rid, clusters[0].records)
    c2 = map(lambda x: x.rid, clusters[1].records)
    print 'Cluster 1:', c1
    print 'Cluster 2:', c2
