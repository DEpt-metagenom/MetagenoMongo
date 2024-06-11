from datetime import datetime
import os
import csv
import difflib
import openpyxl
import re
import PySimpleGUI as sg

# Function to read headers from a CSV file
def load_headers(filename):
    if not os.path.exists(filename):
        sg.popup_error(f"File {filename} not found!")
        return []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        headers = [row[0] for row in reader if not row[0].startswith("#")]
    return headers[1:]  # Skip the first non-header line

# Function to load options from the CSV file
def load_options(filename):
    if not os.path.exists(filename):
        sg.popup_error(f"File {filename} not found!")
        return {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the first row
        options = {}
        for row in reader:
            header = row[0]
            options[header] = {
                'type': row[1],
                'options': row[2].split(',') if row[2] else [],
                'combobox_type': row[3] if len(row) > 3 else ''
            }
    return options

# Get the directory of the script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to headers.csv
headers_file = os.path.join(script_dir, '.metagenomongo.csv')

# Load headers from the CSV file
headers = load_headers(headers_file)

# Load options from the CSV file
options = load_options(headers_file)

# Check if headers were successfully loaded
if not headers:
    sg.popup_error("Headers could not be loaded. Please check the .metagenomongo.csv file.")
    exit(1)

# Initialize an empty data list and empty selected row list
data = []

# Generate the layout
sg.theme('Default1')
layout = [
    [
        sg.Column([
            [sg.Text('Metageno', font=('Segoe UI', 22), justification='left', pad=(0, 0)),
             sg.Text('Mongo', font=('Segoe UI', 22, 'bold'), justification='left', pad=(0, 0)),
             sg.Button('?', key='-HELP-', size=(1, 1), button_color=('white', 'blue'))],
            [sg.Button('Add/Update Data', pad=(0, 10), key='-ADD-', button_color=('white', 'green')),
             sg.Button('Duplicate Entry', pad=(10, 10), key='-DUPLICATE-'),
             sg.Button('Delete Entry', pad=(0, 10), key='-DELETEENTRY-'),
             sg.Button('Correct', pad=(10, 10), key='-CORRECT-', button_color=('white', 'blue')),
             sg.Button('Import File', pad=(0, 10), key='-IMPORT-'),
             sg.Button('Save as CSV', pad=(10, 10), key='-SAVE-'),
             sg.Button('Clear', pad=(0, 10), key='-CLEAR-'),
             sg.Button('Generate template', pad=(10, 10), key='-TEMPLATE-')]
        ])
    ],
    [
        sg.Column([
            [sg.Text(f'{header}:', size=(15, 1), font=('Helvetica', 12), tooltip=header), 
             sg.InputText(key=f'-{header}-', size=(17, 1), readonly=True) if not options[header]['options'] and options[header]['combobox_type'] == 'fix' else
             sg.InputText(key=f'-{header}-', size=(17, 1)) if options[header]['type'] == 'String' and not options[header]['options'] else
             sg.Combo(options[header]['options'], key=f'-{header}-', readonly=(options[header]['combobox_type'] == 'fix'), size=(15, 1)) if options[header]['options'] else
             sg.InputText(key=f'-{header}-', size=(17, 1))]
            for header in headers], size=(300, None), scrollable=True, vertical_scroll_only=True),
        sg.Column([
            [sg.Table(values=data, headings=headers, key='-TABLE-', enable_events=True, 
                      justification='center', auto_size_columns=True, vertical_scroll_only=False, font=('Helvetica', 12), num_rows=50, pad=(0, 0))]
        ], expand_x=True, expand_y=True)
    ]
]

# Create the window with resizable option and set the size to 800x600
window = sg.Window('MetagenoMongo v1.0', layout, resizable=True, size=(800, 600))

# Event loop
while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

    elif event == '-HELP-':
        sg.popup('- - - - - MetagenoMongo help menu - - - - -\n\nThe header files are located in\n.metagenomongo.csv file.', title='MetagenoMongo v1.0', font=('Arial', 12))

    elif event == '-TABLE-':
        selected_rows = values['-TABLE-']
        if selected_rows:
            selected_row = selected_rows[0]  # Take the first selected row
            for i, header in enumerate(headers):
                window['-' + header + '-'].update(value=data[selected_row][i])
        else:
            for header in headers:
                window['-' + header + '-'].update('')

    elif event == '-ADD-':
        entry = [values['-' + header + '-'].replace(".", "-") if values['-' + header + '-'] and header in ["collection_date", "run_date"] else values['-' + header + '-'] for header in headers]

        invalid_date_found = any(header in ["collection_date", "run_date"] and entry[i] and not re.match(r'\d{4}-\d{2}-\d{2}', entry[i]) for i, header in enumerate(headers))
        
        if invalid_date_found:
            sg.popup_error('Invalid date format. Please use YYYY-MM-DD format.', title='Error', font=('Arial', 12))
        elif any(entry):
            selected_row = values['-TABLE-'][0] if values['-TABLE-'] else None
            if selected_row is not None:
                data[selected_row] = entry
            else:
                data.append(entry)
            window['-TABLE-'].update(values=data)
            for header in headers:
                window['-' + header + '-'].update('')
        else:
            sg.popup('Please add some data to the table.', title='Missing Data', font=('Arial', 12), keep_on_top=True)

    elif event == '-DUPLICATE-':
        selected_row = values['-TABLE-'][0] if values['-TABLE-'] else None
        if selected_row is not None:
            duplicated_entry = data[selected_row][:]
            data.append(duplicated_entry)
            window['-TABLE-'].update(values=data)
        else:
            sg.popup('Please select a row to duplicate.', title='No Row Selected', font=('Arial', 12), keep_on_top=True)

    elif event == '-DELETEENTRY-':
        selected_row = values['-TABLE-'][0] if values['-TABLE-'] else None
        if selected_row is not None:
            del data[selected_row]
            window['-TABLE-'].update(values=data)

    elif event == '-TEMPLATE-':
        filename = sg.popup_get_file('Save Template As', save_as=True, file_types=(("CSV Files", "*.csv"),), keep_on_top=True)
        if filename:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
    
    elif event == '-CORRECT-':
        corrected_count = 0
        correction_applied = True
        corrected_items = []
        invalid_date_count = 0
        invalid_combobox_count = 0

        while correction_applied:
            correction_applied = False

            for row_index, row in enumerate(data):
                for col_index, cell in enumerate(row):
                    if isinstance(cell, str):  # Check if the cell is a string before applying string operations
                        corrected_cell = cell.strip(',; ')
                        corrected_cell = re.sub(r'\s+', ' ', corrected_cell)
                        corrected_cell = re.sub(r',\s*(\S)', r'; \1', corrected_cell)
                        if headers[col_index] == "locality":
                            corrected_cell = re.sub(r':(?!\s)', ': ', corrected_cell)
                        if headers[col_index] == "source_type":
                            corrected_cell = corrected_cell.capitalize()
                        if headers[col_index] == "if_repeated":
                            if corrected_cell.lower() == "yes":
                                corrected_cell = "y"
                            elif corrected_cell.lower() == "no":
                                corrected_cell = "n"
                        if corrected_cell != cell:
                            data[row_index][col_index] = corrected_cell
                            corrected_count += 1
                            corrected_items.append(f'Row {row_index + 1}, Column {col_index + 1}: {cell} -> {corrected_cell}')
                            correction_applied = True
                    elif isinstance(cell, datetime.datetime):  # Handle datetime objects separately
                        corrected_cell = cell.strftime('%Y-%m-%d %H:%M:%S')  # Convert datetime to string
                        if corrected_cell != cell:
                            data[row_index][col_index] = corrected_cell
                            corrected_count += 1
                            corrected_items.append(f'Row {row_index + 1}, Column {col_index + 1}: {cell} -> {corrected_cell}')
                            correction_applied = True

        for row_index, row in enumerate(data):
            for col_index, cell in enumerate(row):
                if isinstance(cell, str):  # Check if the cell is a string
                    if headers[col_index] in ["collection_date", "run_date"]:
                        if cell:
                            if not re.match(r'\d{4}-\d{2}-\d{2}', cell):
                                invalid_date_count += 1
                    if headers[col_index] in options and 'options' in options[headers[col_index]]:
                        if cell not in options[headers[col_index]]['options']:
                            invalid_combobox_count += 1

        data = [row for row in data if any(cell.strip() for cell in row)]
        window['-TABLE-'].update(values=data)

        if corrected_count == 0 and invalid_date_count == 0 and invalid_combobox_count == 0:
            sg.popup('Data is correct.', title='Correction Result', keep_on_top=True)
        else:
            corrected_text = '\n'.join(corrected_items)
            correction_count_text = f'Corrected rows: {corrected_count}\nNumber of cells with invalid date: {invalid_date_count}\nNumber of cells with invalid fixed data options: {invalid_combobox_count}'
            multiline_layout = [
                [sg.Text(correction_count_text)],
                [sg.Multiline(corrected_text, size=(50, 10), disabled=True, autoscroll=True)],
                [sg.Button('Close', key='-CLOSE-')]
            ]
            correction_popup = sg.Window('Correction Result', multiline_layout, modal=True, resizable=True, keep_on_top=True)
            while True:
                event, _ = correction_popup.read()
                if event in (sg.WINDOW_CLOSED, '-CLOSE-'):
                    break
            correction_popup.close()


    elif event == '-IMPORT-':
        filename = sg.popup_get_file('Select file to import', file_types=(("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")), keep_on_top=True)
        if filename:
            if filename.endswith(('.csv', '.xlsx')):
                data.clear()
                window['-TABLE-'].update(values=[])
                temp_data = []
                if filename.endswith('.csv'):
                    with open(filename, 'r', newline='', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        header_row = next(reader)
                        for row in reader:
                            temp_data.append(list(row))
                else:
                    workbook = openpyxl.load_workbook(filename)
                    sheet = workbook.active
                    header_row = [cell.value for cell in sheet[1]]
                    for row in sheet.iter_rows(min_row=2, values_only=True):
                        if any(cell for cell in row):
                            temp_data.append(list(row))
                        else:
                            break

                missing_headers = [header for header in header_row if header not in headers and header is not None]
                if missing_headers:
                    suggestion_layout = [
                        [sg.Text(f"The following headers from the imported file are not recognized:\n" + "\n".join(missing_headers))],
                        *[[sg.Text(f"{header}: "), sg.Combo(headers, key=f'-{header}-suggestion', default_value=difflib.get_close_matches(header, headers)[0] if difflib.get_close_matches(header, headers) else header, size=(30, 1), readonly=True)] for header in missing_headers],
                        [sg.Button('No, I will correct manually', key='-NO-'), sg.Button('Yes, replace automatically', key='-YES-')]
                    ]
                    suggestion_popup = sg.Window('Header Suggestions', suggestion_layout, modal=True, keep_on_top=True)
                    event, values = suggestion_popup.read()
                    suggestion_popup.close()
                    if event == '-YES-':
                        header_mapping = {header: values[f'-{header}-suggestion'] for header in missing_headers}
                        data.clear()
                        for row in temp_data:
                            new_row = ['' for _ in headers]
                            for header in headers:
                                closest_match = difflib.get_close_matches(header, header_row)
                                if closest_match:
                                    selected_header = header_mapping.get(closest_match[0], closest_match[0])
                                    header_index = header_row.index(closest_match[0])
                                    cell_value = row[header_index]
                                    if cell_value.strip():
                                        new_row[headers.index(selected_header)] = cell_value
                            data.append(new_row)
                else:
                    for row in temp_data:
                        data.append([row[header_row.index(header)] if header in header_row else '' for header in headers])

                window['-TABLE-'].update(values=data)

    elif event == '-SAVE-':
        filename = sg.popup_get_file('Save File', save_as=True, file_types=(("CSV Files", "*.csv"),), keep_on_top=True)
        if filename:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(headers)
                writer.writerows(data)

    elif event == '-CLEAR-':
        for header in headers:
            window['-' + header + '-'].update('')
        window['-TABLE-'].update(values=[])
        data.clear()

# Close the window
window.close()
