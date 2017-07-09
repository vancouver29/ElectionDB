#!/usr/bin/python
import psycopg2
from config import db_config
import datetime, time
import csv


if __name__ == '__main__':

    conn = None

    try:
        print "connecting to DB..."
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()

        # get tag counts
        sql =   """
                SELECT tag, COUNT(*)
                FROM Hashtags
                GROUP BY tag
                ORDER BY tag ASC
                """

        cur.execute(sql)
        tag_counts = cur.fetchall()

        f = open('data.csv', 'wb')
        writer = csv.writer(f)

        # calculate average timestamps
        for (tag, count) in tag_counts:
            sql =   """
                    SELECT tweet_time
                    FROM Hashtags
                    WHERE tag = %s;
                    """

            cur.execute(sql, (tag,))
            t_stamps = cur.fetchall()
            t_stamps = map(lambda x: time.mktime(x[0].timetuple()), t_stamps)
            avg_time = sum(t_stamps) / count
            # writer.writerow((tag, str(count), str(avg_time)))
            writer.writerow((str(avg_time), str(count)))


    except (Exception, psycopg2.DatabaseError) as e:
        print "ERROR:", e

    finally:
        f.close()
        if conn is not None:
            conn.close()
