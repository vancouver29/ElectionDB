#!/usr/bin/python
import psycopg2
from config import db_config

table_commands = (
    """
    DROP TABLE IF EXISTS Tweets CASCADE;
    DROP TABLE IF EXISTS Hashtags;
    DROP DOMAIN IF EXISTS HANDLE_TYPE;
    DROP DOMAIN IF EXISTS NATURAL_NUM;
    """,
    """
    CREATE DOMAIN HANDLE_TYPE AS VARCHAR(15) CHECK (VALUE ~ '^\w{1,15}$');
    CREATE DOMAIN NATURAL_NUM AS INTEGER NOT NULL CHECK (VALUE >= 0);
    """,
    """
    CREATE TABLE Tweets (
        handle          HANDLE_TYPE     NOT NULL,
        content         VARCHAR(140)    NOT NULL,
        t_stamp         TIMESTAMP       NOT NULL,
        is_retweet      BOOLEAN         NOT NULL,
        orig_author     HANDLE_TYPE,
        retweet_count   NATURAL_NUM,
        fav_count       NATURAL_NUM,
        PRIMARY KEY (handle, t_stamp)
    );
    """,
    """
    CREATE TABLE Hashtags (
        tag           VARCHAR(140)  NOT NULL CHECK (tag ~ '^#\w*[a-zA-Z]\w*$'),
        tweet_handle  HANDLE_TYPE   NOT NULL,
        tweet_t_stamp TIMESTAMP     NOT NULL,
        PRIMARY KEY (tag, tweet_handle, tweet_t_stamp),
        FOREIGN KEY (tweet_handle, tweet_t_stamp)
        REFERENCES Tweets(handle, t_stamp)
        ON UPDATE CASCADE ON DELETE CASCADE
    );
    """
)

def create_tables():

    conn = None

    try:
        # connect to the PostgreSQL server
        print "\nconnecting to DB.."
        # get DB info
        params = db_config()
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # execute commmands
        print "creating tables..."
        for command in table_commands:
            cur.execute(command)

        # commit the changes
        conn.commit()
        cur.close()
        print "DONE"

    except (Exception, psycopg2.DatabaseError) as error:
        print "ERROR:", error

    finally:
        if conn is not None:
            conn.close()
