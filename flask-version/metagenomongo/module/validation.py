import re
from datetime import datetime
from collections import Counter

DATE_FIELDS = ["collection_date", "run_date"]
MANDATORY_COLUMNS = ("projectID", "project_directory", "sampleID")
date_pattern = re.compile(r'^\d{4}(-\d{2}(-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{3}Z)?)?)?$')
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
    error_list =[]
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
    print(f"validate")
    if data == []:
        error_list.append([0, "", "Empty data."])
        print(f"data {data}")
    for row_index, row in enumerate(data):
        sampleID, run_directory, barcode = "", "", ""
        for col_index, cell in enumerate(row):
            field = fields[col_index]
            print(f"field:{field}")
            if isinstance(cell, str):
                if field in DATE_FIELDS:
                    if field == "run_date" and cell == "":
                        continue
                    elif not date_pattern.match(cell):
                        error_list.append([row_index, field, "Invalid value. Expected data type: date"])
                if field in options and options[field]['combobox_type'] == 'fix' and options[field]['options']:
                    if cell not in options[field]['options']:
                        error_list.append([row_index, field, f"Invalid value. Possible values are: '{options[field]['options']}'"])
                if field in int_dynamic_type:
                    if cell != "":
                        if not cell.isdigit():
                            error_list.append([row_index, field, "Invalid value. Expected data type: int"])
                if field in float_dynamic_type:
                    if cell != "":
                        try:
                            float(cell)
                        except ValueError:
                            error_list.append([row_index, field, "Invalid value. Expected data type: float"])
                if field == "sampleID":
                    sampleID = cell
                    if sampleID != "":
                        sampleID_list.append(sampleID)
                if field == "run_directory" and sampleID != "":
                    run_directory = cell
                if field == "barcode" and sampleID != "":
                    barcode = cell
                if field in MANDATORY_COLUMNS and cell == "":
                    error_list.append([row_index, field, f"{field} is necessary"])
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
                            error_list.append([row_index, field, "run_directory is necessary"])
                        run_directory = cell
                    if field == "barcode":
                        if cell == "":
                            error_list.append([row_index, field, "Barcode is necessary"])
                        barcode = cell
            if f"{sampleID}{run_directory}{barcode}" in duplicate_sampleID_rundirectory_barcodes:
                error_list.append([row_index, field, "Each pair of sampleID,rundirectory,barcode must be unique"])
    errors['fatal_error'] = error_list