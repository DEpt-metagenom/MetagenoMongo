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