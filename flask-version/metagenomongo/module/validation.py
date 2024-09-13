import re
from datetime import datetime
from collections import Counter

DATE_FIELDS = ["collection_date", "run_date"]
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{3}Z)?$') 
# accepted formats are YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.fffZ
def data_assign(fields, values):
    # Retrieve input values
    result = {}
    result = {"data": [list(values.values())]}
    result["data"][0].insert(0, '') # Duplicate
    result["data"][0].insert(0, '') # Delete
    result["data"][0].pop() # Duplicate
    result["data"][0].pop() # Delete
    return result

def create_data_type_set(data_type, fields, options):
    return {field for field in fields if data_type == options[field]['datatype']}

def validation_all(fields, options, errors, df_temp):
    # Remove fully empty rows
    df_temp = df_temp[~(df_temp == '').all(axis=1)]
    corrected_count = 0
    corrected_items = []
    invalid_date_messages = []
    invalid_combobox_messages = []
    data = df_temp.values.tolist()
    int_dynamic_type = create_data_type_set("int", fields, options)
    float_dynamic_type = create_data_type_set("float", fields, options)
    sampleID_rundirectory_barcode_list = []
    sampleID_list = []
    # Apply corrections to data
    for row_index, row in enumerate(data):
        for col_index, cell in enumerate(row):
            if isinstance(cell, str):  # Process only strings
                original_cell = cell
                cell = re.sub(r'\s+', ' ', cell)
                cell = cell.strip(',; ')
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
    # Validate data
    for row_index, row in enumerate(data):
        sampleID, run_directory, barcode = "", "", ""
        for col_index, cell in enumerate(row):
            field = fields[col_index]
            if isinstance(cell, str):
                if field in DATE_FIELDS:
                    if field == "run_date" and cell == "":
                        continue
                    elif not date_pattern.match(cell):
                        invalid_date_messages.append(f"Invalid value in row {row_index + 1}, column '{field}': Expected data type: date")
                if field in options and options[field]['combobox_type'] == 'fix' and options[field]['options']:
                    if cell not in options[field]['options']:
                        invalid_combobox_messages.append(f"Invalid value in row {row_index + 1}, column '{field}': Possible values are: '{options[field]['options']}'")
                if field in int_dynamic_type:
                    if cell != "":
                        if not cell.isdigit():
                            invalid_combobox_messages.append(\
                            f"Invalid data type in row {row_index + 1}, column '{field}': Expected data type: int")
                if field in float_dynamic_type:
                    if cell != "":
                        try:
                            float(cell)
                        except ValueError:
                            invalid_combobox_messages.append(\
                            f"Invalid data type in row {row_index + 1}, column '{field}': Expected data type: float")
                if field == "sampleID":
                    sampleID = cell
                    if sampleID == "":
                        invalid_combobox_messages.append(\
                            f"SampleID is necessary in row {row_index + 1}, column '{field}':")
                    else:
                        sampleID_list.append(sampleID)
                if field == "run_directory" and sampleID != "":
                    run_directory = cell
                if field == "barcode" and sampleID != "":
                    barcode = cell
        if sampleID != "":
            data_id = f"{sampleID}{run_directory}{barcode}"
            sampleID_rundirectory_barcode_list.append(data_id)
    sampleIDs = Counter(sampleID_list)
    sampleID_rundirectory_barcode_ids = Counter(sampleID_rundirectory_barcode_list)
    duplicate_sampleIDs = {id for id, count in sampleIDs.items() if int(count) > 1}
    duplicate_sampleID_rundirectory_barcodes = \
        {id for id, count in sampleID_rundirectory_barcode_ids.items() if int(count) > 1}
    if duplicate_sampleIDs != {}:
        for row_index, row in enumerate(data):
            sampleID, run_directory, barcode = "", "", ""
            for col_index, cell in enumerate(row):
                field = fields[col_index]
                if cell in duplicate_sampleIDs:
                    sampleID = cell
                if sampleID != "":
                    if field == "run_directory":
                        if cell == "":
                            invalid_combobox_messages.append(\
                                f"run_directory is necessary in row {row_index + 1}, column '{field}':")                   
                        run_directory = cell
                    if field == "barcode":
                        if cell == "":
                            invalid_combobox_messages.append(\
                                f"Barcode is necessary in row {row_index + 1}, column '{field}':")
                        barcode = cell
            if f"{sampleID}{run_directory}{barcode}" in duplicate_sampleID_rundirectory_barcodes:
                invalid_combobox_messages.append(\
                            f"sampleID_rundirectory_barcodes must be unique in row {row_index + 1}:")
    # Prepare result text
    if len(invalid_date_messages) != 0 or len(invalid_combobox_messages) != 0:
        result_text = (
                    f'Number of cells with invalid date: {len(invalid_date_messages)}\n'
                    # f'Number of cells with invalid fixed data options: {len(invalid_combobox_messages)}\n'
                    )
        # Add detailed errors
        detailed_errors = '\n'.join(invalid_date_messages + invalid_combobox_messages)
        result_text += detailed_errors
        errors['fatal_error'].append(result_text)