#!/usr/bin/python
import psycopg2
from config import db_config
from time import mktime
from datetime import datetime
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

# returns the tag occurrence count for the given date string,
# (expected to be in the form: "YYYY-MM-DD").
#
def tagFrequencyFor(day):

    conn = None
    occurrences = None

    try:
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # tags & freqency count between two dates
        sql =   """
                SELECT tag, Count(*)
                FROM Hashtags
                WHERE tweet_time >= %s AND tweet_time <= %s
                GROUP BY tag
                """

        startTime = day + " 00:00:00"
        endTime = day + " 23:59:59"

        cur.execute(sql, (startTime, endTime))
        occurrences = cur.fetchall()

    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        if conn is not None:
            conn.close()

    return occurrences



if __name__ == '__main__':

    # day ranges for dataset
    jan = range(5, 32)
    feb = range(1, 30)
    mar = range(1, 32)
    apr = range(1, 31)
    may = range(1, 32)
    jun = range(1, 31)
    jul = range(1, 32)
    aug = range(1, 32)
    sep = range(1, 28)

    months = [jan, feb, mar, apr, may, jun , jul, aug, sep]

    # key: tag, val: [ {'date': timestamp, 'count': integer} ]
    data = dict()
    total = 0
    days = 0
    highestCount = 0
    dateStrings = list()
    hashtags = listOfHashtags()

    # generate all date strings
    for i, month in enumerate(months):
        for day in month:
            days += 1
            # build date string "YYYY-MM-DD"
            dateStr = "-".join(["2016", str(i+1), str(day)])
            timestamp = mktime(datetime.strptime(dateStr, "%Y-%m-%d").timetuple()) * 1000

            freqs = tagFrequencyFor(dateStr)

            # for tags that don't occur on this date
            for tag in hashtags:
                if tag not in map(lambda x: x[0], freqs):
                    data.setdefault(tag, list()).append({"date": dateStr, "timestamp": timestamp, "count": 0})

            # for tags that do
            for tag, count in freqs:
                data.setdefault(tag, list()).append({"date": dateStr, "timestamp": timestamp, "count": count})
                total += count
                if count > highestCount:
                    highestCount = count

    print 'highestCount:', highestCount
    print 'number of days:', days
    print "total keys:", len(data.keys())
    print "total occurrences:", total

    # create json file
    with open('frequency.json', 'w') as outfile:
        # convert data to json format
        finalData = []
        for tag, counts in data.items():
            finalData.append({'id': tag, 'data': counts})

        s = json.dumps(finalData, indent=4, separators=(',',':'), sort_keys=True)
        # write to the file
        outfile.write(s)
