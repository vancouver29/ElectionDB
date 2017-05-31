#!/usr/bin/python
from data_cleaner import clean_data
from table_creator import create_tables
from table_populator import populate_tables

if __name__ == '__main__':
    clean_data()
    create_tables()
    populate_tables()
