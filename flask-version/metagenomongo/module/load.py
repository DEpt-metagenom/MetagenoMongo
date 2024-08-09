import os
import csv
import pandas as pd

def load_options(filename):
    if not os.path.exists(filename):
        # sg.popup_error(f"File {filename} not found!")
        return {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        options = {}
        for row in reader:
            field = row[0].strip()
            options[field] = {
                'datatype': row[1], # str, int, float, date
                'options': row[2].split(',') if row[2] else [], # empty or options within quotation marks
                'combobox_type': row[3] # fix, dynamic
            }
    return options