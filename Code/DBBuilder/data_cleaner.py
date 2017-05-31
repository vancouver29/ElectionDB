#!/usr/bin/python
from openpyxl import Workbook
from openpyxl import load_workbook
from config import data_config

def clean_row(data):
    # convert encoded symbols
    data[1] = data[1].replace("&amp;", "&")
    data[1] = data[1].replace("&lt;", "<")
    data[1] = data[1].replace("&gt;", ">")
    # reformat time stamp
    data[4] = data[4].replace("T"," ")
    # return only needed columns
    return data[:2] + data[4:5] + data[2:4] + data[7:9]

def clean_data():
    # open raw data file & get the worksheet
    input_file = data_config['input_filename']
    print '\nopening file:', input_file, '...'
    input_wb = load_workbook(input_file, read_only = True)
    input_ws = input_wb[data_config['sheet_name']]

    # create new workbook with a new worksheet
    output_wb = Workbook()
    output_ws = output_wb.active
    output_ws.title = data_config['sheet_name']

    print 'cleaning data...'
    # for each row in input sheet
    for row in list(input_ws.rows):
        # extract cell data
        row_data = []
        for cell in row:
            row_data.append(cell.value)
        # clean the data & add to new sheet
        output_ws.append(clean_row(row_data))

    # save wb
    output_wb.save(filename = data_config['clean_filename'])
    print 'DONE: saved file:', data_config['clean_filename']
