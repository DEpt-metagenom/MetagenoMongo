import os
import csv
import re
from datetime import datetime
import pandas as pd
import PySimpleGUI as sg

def load_headers(filename):
    if not os.path.exists(filename):
        sg.popup_error(f"File {filename} not found!")
        return []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        headers = [row[0] for row in reader if not row[0].startswith("#")]
    return headers[1:] # Skip the header row

def load_options(filename):
    if not os.path.exists(filename):
        sg.popup_error(f"File {filename} not found!")
        return {}
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        options = {}
        for row in reader:
            header = row[0] # column name
            options[header] = {
                'datatype': row[1], # str, int, float, date
                'options': row[2].split(',') if row[2] else [], # empty or options within quotation marks
                'combobox_type': row[3] # fix, dynamic
            }
    return options

script_dir = os.path.dirname(os.path.abspath(__file__))
headers_file = os.path.join(script_dir, '.metagenomongo.csv')

headers = load_headers(headers_file)
options = load_options(headers_file)

if not headers:
    sg.popup_error("Headers could not be loaded. Please check the .metagenomongo.csv file.")
    exit(1)

data = []

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
            [
                sg.Text(f'{header}:', size=(15, 1), font=('Helvetica', 12), tooltip=header),
                sg.InputText(key=f'-{header}-', size=(17, 1), readonly=True) if not options[header]['options'] and options[header]['combobox_type'] == 'fix' else
                sg.InputText(key=f'-{header}-', size=(17, 1)) if options[header]['datatype'] == 'str' and not options[header]['options'] else
                sg.Combo(options[header]['options'], key=f'-{header}-', readonly=(options[header]['combobox_type'] == 'fix'), size=(15, 1)) if options[header]['options'] else
                sg.InputText(key=f'-{header}-', size=(17, 1))
            ]
            for header in headers
        ], size=(300, None), scrollable=True, vertical_scroll_only=True),
        sg.Column([
            [sg.Table(values=data, headings=headers, key='-TABLE-', enable_events=True, 
                      justification='center', auto_size_columns=True, vertical_scroll_only=False, font=('Helvetica', 12), num_rows=50, pad=(0, 0))]
        ], expand_x=True, expand_y=True)
    ]
]

window = sg.Window('MetagenoMongo v1.0', layout, resizable=True, size=(800, 600))

date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{3}Z)?$') # accepted formats are YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.fffZ

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        try:
            datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            return True
        except ValueError:
            return False

while True:
    event, values = window.read()
    if event in (sg.WINDOW_CLOSED, 'Exit'):
        break

    elif event == '-HELP-':
        sg.popup('- - - - - MetagenoMongo help menu - - - - -\n\nThe header files are located in\n.metagenomongo.csv file.', title='MetagenoMongo v1.0', font=('Arial', 12))

    elif event == '-ADD-':
        # Retrieve input values
        new_entry = []
        all_empty = True  # Flag to track if all input fields are empty
        valid = False  # Flag to track if any valid input fields are found
        for header in headers:
            value = values[f'-{header}-']
            if value:  # Non-empty field found
                all_empty = False
                valid = True
                datatype = options[header]['datatype']
                if datatype == 'int':
                    if not value.isdigit():
                        sg.popup_error(f"{header} must be an integer")
                        valid = False
                        break
                elif datatype == 'float':
                    try:
                        float(value)
                    except ValueError:
                        sg.popup_error(f"{header} must be a float")
                        valid = False
                        break
                elif datatype == 'date':
                    if not date_pattern.match(value) or not is_valid_date(value):
                        sg.popup_error(f"{header} must be in a valid YYYY-MM-DD format")
                        valid = False
                        break
            new_entry.append(value)

        if all_empty:
            sg.popup('Please add some data to the table.', title='Missing Data', font=('Arial', 12), keep_on_top=True)
        elif valid:  # Only add/update if at least one valid input field is found
            # Check if updating an existing entry
            selected_rows = values['-TABLE-']
            if selected_rows:
                # Update the selected row
                data[selected_rows[0]] = new_entry
            else:
                # Add new entry
                data.append(new_entry)
            
            # Update the table
            window['-TABLE-'].update(values=data)

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

    elif event == '-CLEAR-':
        for header in headers:
            window['-' + header + '-'].update('')
        window['-TABLE-'].update(values=[])
        data.clear()

    elif event == '-SAVE-':
        # Prompt user for file save location
        save_filename = sg.popup_get_file('Save File', save_as=True, file_types=(("CSV Files", "*.csv"),))
        if save_filename:
            # Determine columns with data
            columns_with_data = [header for header in headers if any(data_row[headers.index(header)] for data_row in data)]

            # Extract and clean data to save
            data_to_save = [columns_with_data]  # Start with header line
            for data_row in data:
                row_to_save = []
                for header in columns_with_data:  # Only iterate over columns with data
                    value = data_row[headers.index(header)].strip() if header in headers else ''
                    row_to_save.append(value)
                data_to_save.append(row_to_save)

            # Write data to CSV file
            with open(save_filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(data_to_save)

            sg.popup(f"Table data saved to {save_filename}", title='Save Successful', font=('Arial', 12), keep_on_top=True)

    elif event == '-IMPORT-':
        import_filename = sg.popup_get_file('Import File', file_types=(("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")), keep_on_top=True)
        if import_filename:
            _, ext = os.path.splitext(import_filename)
            if ext == '.csv':
                df_temp = pd.read_csv(import_filename, dtype=str)  # Load as strings
            elif ext == '.xlsx':
                df_temp = pd.read_excel(import_filename, dtype=str)  # Load as strings
            else:
                sg.popup_error(f"Unsupported file format: {ext}. Please select a CSV or Excel file.")
                continue

            # Strip whitespace from headers
            df_temp.columns = df_temp.columns.str.strip()
            
            # Strip whitespace from data
            df_temp = df_temp.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            
            # Replace NaN with empty strings
            df_temp = df_temp.fillna('')
            
            # Remove fully empty rows
            df_temp = df_temp[~(df_temp == '').all(axis=1)]

            # Ensure headers match with .metagenomongo.csv headers
            script_dir = os.path.dirname(os.path.abspath(__file__))
            headers_file = os.path.join(script_dir, '.metagenomongo.csv')
            expected_headers = load_headers(headers_file)
            
            # Get actual headers from the temporary DataFrame
            imported_headers = list(df_temp.columns)
            
            # Identify headers in the input file that do not appear in the expected headers
            incorrect_headers = [header for header in imported_headers if header not in expected_headers]
            
            if incorrect_headers:
                # Layout for header correction
                suggestion_layout = [
                    [sg.Text(f"The following headers from the imported file do not match the expected headers:\n" + "\n".join(incorrect_headers))],
                    [sg.Text("Please select the correct header for each mismatched header:")]
                ]
                
                # Create dropdowns for each incorrect header
                for header in incorrect_headers:
                    suggestion_layout.append([sg.Text(f"{header}: "), sg.Combo(expected_headers, size=(30, 1), key=f'-{header}-suggestion', readonly=True)])
                
                suggestion_layout.append([sg.Button('Cancel', key='-CANCEL-'), sg.Button('Apply Changes', key='-APPLY-')])
                
                suggestion_popup = sg.Window('Header Suggestions', suggestion_layout, modal=True, keep_on_top=True)
                event, values = suggestion_popup.read()
                suggestion_popup.close()
                
                if event == '-APPLY-':
                    header_mapping = {header: values[f'-{header}-suggestion'] for header in incorrect_headers}
                    
                    # Rename the incorrect headers to the selected headers in the DataFrame
                    df_temp.rename(columns=header_mapping, inplace=True)
                    
                    # Remove duplicate columns if they exist
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                    
                    # Reindex df_temp to match the expected headers, filling missing columns with empty strings
                    df_temp = df_temp.reindex(columns=expected_headers, fill_value='')
                    
                    # Remove fully empty rows
                    df_temp = df_temp[~(df_temp == '').all(axis=1)]
                    
                    data = df_temp.values.tolist()
                    
                    # Update the table
                    window['-TABLE-'].update(values=data, num_rows=50)
                    sg.popup('Data imported successfully with header mapping.', title='Import Successful', font=('Arial', 12), keep_on_top=True)
                else:
                    sg.popup_error('Import cancelled. Please correct the headers manually and try again.', keep_on_top=True)
            else:
                # No incorrect headers, just update the table
                df_temp = df_temp.reindex(columns=expected_headers, fill_value='')  # Ensure columns match the expected headers
                df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]  # Remove any duplicate columns
                
                # Remove fully empty rows
                df_temp = df_temp[~(df_temp == '').all(axis=1)]
                
                data = df_temp.values.tolist()
                
                # Update the table
                window['-TABLE-'].update(values=data, num_rows=50)
                sg.popup('Data imported successfully.', title='Import Successful', font=('Arial', 12), keep_on_top=True)

    elif event == '-TABLE-':
        selected_rows = values['-TABLE-']
        if selected_rows:
            selected_row = selected_rows[0]  # Take the first selected row
            for i, header in enumerate(headers):
                window['-' + header + '-'].update(value=data[selected_row][i])
        else:
            for header in headers:
                window['-' + header + '-'].update('')

window.close()
