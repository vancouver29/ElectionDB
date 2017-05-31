#!/usr/bin/python
from getpass import getpass

def db_config():
    database = 'election'
    user = 'johnnguyen'
    password = getpass()
    return {'database': database, 'user': user, 'password': password}

data_config = { 'input_filename'    : 'data/election-tweet-data-raw.xlsx',
                'clean_filename'    : 'data/election-tweet-data-clean.xlsx',
                'sheet_name'        : 'american-election-tweets' }
