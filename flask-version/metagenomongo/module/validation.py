import re
from datetime import datetime
# return number  number:message 
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{3}Z)?$') 
# accepted formats are YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.fffZ
def data_type_validation(fields, options, values):
    # Retrieve input values
    data = []
    new_entry = []
    result = {}
    all_empty = True  # Flag to track if all input fields are empty
    valid = False  # Flag to track if any valid input fields are found
    for field in fields:
        value = values[field]
        if value:  # Non-empty field found
            # print(value) ok skip empty field
            all_empty = False
            valid = True
            datatype = options[field]['datatype']
            # print(datatype) ok
            if datatype == 'int':
                if not value.isdigit():
                    valid = False
                    result["column"] = field
                    result["error"] = "integer type"
                    break
            elif datatype == 'float':
                try:
                    float(value)
                except ValueError:
                    valid = False
                    result["column"] = field
                    result["error"] = "float type"
                    break
            elif datatype == 'date':
                if not date_pattern.match(value) or not is_valid_date(value):
                    valid = False
                    result["column"] = field
                    result["error"] = "date format"
                    break
        new_entry.append(value)
    if all_empty:
        result["error"] = "Please add some data to the table."
    
    # elif valid:  # Only add/update if at least one valid input field is found
    #     # Check if updating an existing entry
    #     selected_rows = values['-TABLE-']
    #     if selected_rows:
    #         # Update the selected row
    #         data[selected_rows[0]] = new_entry
    #     else:
    #         # Add new entry
    #         data.append(new_entry)
    if valid:
        data.append(new_entry)
    # else:
    #     return result
    result["data"]=data
    return result

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

def validation_all(expected_headers, fields, options, results, df_temp):
    df_temp = df_temp.reindex(columns=expected_headers, fill_value='')  # Ensure columns match the expected headers
    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]  # Remove any duplicate columns
                    
                    # Remove fully empty rows
    df_temp = df_temp[~(df_temp == '').all(axis=1)]
                    
    data_tolist = df_temp.values.tolist()
    data = df_temp
    corrected_count = 0
    corrected_items = []
    invalid_date_messages = []
    invalid_combobox_messages = []
    data = df_temp.values.tolist()
    # Apply corrections to data
    for row_index, row in enumerate(data):
        for col_index, cell in enumerate(row):
            if isinstance(cell, str):  # Process only strings
                original_cell = cell
                cell = cell.strip(',; ')
                cell = re.sub(r'\s+', ' ', cell)
                cell = re.sub(r',\s*(\S)', r'; \1', cell)
                
                # Apply specific column corrections
                if fields[col_index] == "locality":
                    cell = re.sub(r':(?!\s)', ': ', cell)
                elif fields[col_index] == "source_type":
                    cell = cell.capitalize()
                elif fields[col_index] == "if_repeated":
                    cell = "y" if cell.lower() == "yes" else "n" if cell.lower() == "no" else cell
                
                if cell != original_cell:
                    data[row_index][col_index] = cell
                    corrected_count += 1
                    corrected_items.append(f'Row {row_index + 1}, Column {col_index + 1}: {original_cell} -> {cell}')
            
            elif isinstance(cell, datetime.datetime):  # Handle datetime objects separately
                original_cell = cell
                cell = cell.strftime('%Y-%m-%d %H:%M:%S')
                if cell != original_cell:
                    data[row_index][col_index] = cell
                    corrected_count += 1
                    corrected_items.append(f'Row {row_index + 1}, Column {col_index + 1}: {original_cell} -> {cell}')
    date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{3}Z)?$') 
    # Validate data
    for row_index, row in enumerate(data):
        for col_index, cell in enumerate(row):
            header = fields[col_index]
            if isinstance(cell, str):
                if header in ["collection_date", "run_date"]:
                    if not date_pattern.match(cell):
                        invalid_date_messages.append(f"Invalid date in row {row_index + 1}, column '{header}': '{cell}'")
                
                if header in options and options[header]['combobox_type'] == 'fix' and options[header]['options']:
                    if cell not in options[header]['options']:
                        invalid_combobox_messages.append(f"Invalid fixed option in row {row_index + 1}, column '{header}': '{cell}'")
    # Remove rows that are entirely empty
    data = [row for row in data if any(cell.strip() for cell in row)]
    # Prepare result text
    if len(invalid_date_messages) != 0:
        result_text = (
                    f'Number of cells with invalid date: {len(invalid_date_messages)}\n'
                    # f'Number of cells with invalid fixed data options: {len(invalid_combobox_messages)}\n'
                    )
        # Add detailed errors
        detailed_errors = '\n'.join(invalid_date_messages + invalid_combobox_messages)
        result_text += detailed_errors
        results.append({'error': result_text})