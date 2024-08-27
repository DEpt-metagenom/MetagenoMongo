import re
from datetime import datetime

DATE_FIELDS = ["collection_date", "run_date"]
date_pattern = re.compile(r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}\.\d{3}Z)?$') 
# accepted formats are YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS.fffZ
def data_assign(fields, values):
    # Retrieve input values
    data = []
    new_entry = []
    result = {}
    all_empty = True  # Flag to track if all input fields are empty
    result = {"data": [list(values.values())]}
    if not any(values.values()):
        result["error"] = "There is no data in the row"
    return result

def create_data_type_list(data_type, fields, options):
    return [field for field in fields if data_type == options[field]['datatype']]

def validation_all(fields, options, results, df_temp):
    # Remove fully empty rows
    df_temp = df_temp[~(df_temp == '').all(axis=1)]
    corrected_count = 0
    corrected_items = []
    invalid_date_messages = []
    invalid_combobox_messages = []
    data = df_temp.values.tolist()
    int_dynamic_type = create_data_type_list("int", fields, options)
    float_dynamic_type = create_data_type_list("float", fields, options)
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
                    if not date_pattern.match(cell):
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
                # check sampleID + run_directory + barcode
                # check sampleID + run_directory + barcode are empty or not
                if field == "sampleID":
                    sampleID = cell
                    if sampleID == "":
                        invalid_combobox_messages.append(\
                            f"SampleID is necessary in row {row_index + 1}, column '{field}':")
                    else:
                        sampleID_list.append(sampleID)
                if field == "run_directory" and sampleID in sampleID_list:
                    run_directory = cell
                if field == "barcode" and sampleID in sampleID_list:
                    barcode = cell
        if sampleID != "":
            data_id = sampleID+run_directory+barcode
            if data_id in sampleID_rundirectory_barcode_list:
                invalid_combobox_messages.append(\
                    f"The combination of SampleID, run_directory and barcode is not unique in row {row_index + 1}:")
            sampleID_rundirectory_barcode_list.append(data_id)

    # Prepare result text
    if len(invalid_date_messages) != 0 or len(invalid_combobox_messages) != 0:
        result_text = (
                    f'Number of cells with invalid date: {len(invalid_date_messages)}\n'
                    # f'Number of cells with invalid fixed data options: {len(invalid_combobox_messages)}\n'
                    )
        # Add detailed errors
        detailed_errors = '\n'.join(invalid_date_messages + invalid_combobox_messages)
        result_text += detailed_errors
        results.append({'error': result_text})