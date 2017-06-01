#!/usr/bin/python
import psycopg2
from config import db_config
from config import data_config
from openpyxl import load_workbook
import re

def populate_tables():

    conn = None
    tweet_count = 0
    hashtag_count = 0

    # open the xlsx spreadsheet containing clean data
    filename = data_config['clean_filename']
    print "\nopening data file:", filename
    wb = load_workbook(filename, read_only = True)
    ws = wb[data_config['sheet_name']]

    # exclude first row (column names)
    rows = list(ws.rows)[1:]
    print "Number of tweets to insert:", len(rows)

    try:
        # connect to the PostgreSQL server
        print "connecting to DB.."
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        print "populating tables..."
        for row in rows:
            # extract cell values from row
            row = map(lambda cell: cell.value, row)
            # insert tweet
            sql = "INSERT INTO Tweets VALUES (%s,%s,%s,%s,%s,%s,%s)"
            cur.execute(sql, row)
            tweet_count += 1

            # get hashtags from tweet
            hashtags = extract_hashtags(row)
            sql = "INSERT INTO Hashtags VALUES (%s,%s,%s)"
            # for each tag
            for tag in hashtags:
                # insert tag, handle, timestamp
                cur.execute(sql, (tag, row[0], row[2]))
                hashtag_count += 1

        # commit the changes
        conn.commit()
        cur.close()
        print "DONE:", tweet_count, "tweets and", hashtag_count, "hashtags inserted.\n"

    except (Exception, psycopg2.DatabaseError) as error:
        print "ERROR:", error

    finally:
        if conn is not None:
            conn.close()


def extract_hashtags(tweet):
    # extract hashtags
    hashtags = re.findall("#\\w*[a-zA-Z]\\w*", tweet[1])
    # remove duplicate tags
    return list(set(hashtags))
