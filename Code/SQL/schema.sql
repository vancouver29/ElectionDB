-- Domains
CREATE DOMAIN HANDLE_TYPE AS VARCHAR(15) CHECK (VALUE ~ '^\w{1,15}$');
CREATE DOMAIN NATURAL_NUM AS INTEGER NOT NULL CHECK (VALUE >= 0);

-- Tweet relation
CREATE TABLE Tweets (
      handle          HANDLE_TYPE     NOT NULL,
      content         VARCHAR(140)    NOT NULL,
      time            TIMESTAMP       NOT NULL,
      is_retweet      BOOLEAN         NOT NULL,
      orig_author     HANDLE_TYPE,
      retweet_count   NATURAL_NUM,
      fav_count       NATURAL_NUM,
      PRIMARY KEY (handle, time)
  );

  -- Hashtags relation
  CREATE TABLE Hashtags (
        tag           VARCHAR(140)  NOT NULL CHECK (tag ~ '^#\w*[a-zA-Z]\w*$'),
        tweet_handle  HANDLE_TYPE   NOT NULL,
        tweet_time    TIMESTAMP     NOT NULL,
        PRIMARY KEY (tag, tweet_handle, tweet_time),
        FOREIGN KEY (tweet_handle, tweet_time)
        REFERENCES Tweets(handle, time)
        ON UPDATE CASCADE ON DELETE CASCADE
    );
