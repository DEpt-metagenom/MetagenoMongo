from flask import Flask, request, render_template, redirect, url_for, flash
import os
import csv
import pandas as pd
from werkzeug.utils import secure_filename
import re
from datetime import datetime

import module.load as load
import module.validation as data_validation

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# fields = ["projectID","sampleID", "specimenID","isolation_source","source_type","species",
# "sex","host","mother","collection_date","collected_by","locality","locality_2",
# "preservation","tissue","comment","platform","sequencing_approach","barcode",
# "run_date","run_directory","project_directory","if_repeated","why_repeated",
# "assembly_method-version","genome_coverage","enrichment_media","DNA_conc",
# "DNA_storage",	"strain_storage",	"subgroup",	"hatchery",	"1st_fase_farm",
# "age","ESBL","AmpC","CarbapenemR","hodge_test","AMP","COX","CRO",
# "CZD","FEP","ERT","PXB","CIP","TET","TGC","SXT","AKN","GMN",
# "TMN","AMC","API","CR","CZA","CL","COL","FOS","GME","IMP",
# "LIN","MRP","NFE","NIT","TEI","VA","PTZ","AMX","CI","CXM",
# "SAM","LEV","mCIM","CT","ColistinMIC","ERTMIC","ETPMIC",
# "IMIMIC","MERMIC","MRPMIC","TEIMIC","VAMIC","ATM","FFC"]

script_dir = os.path.dirname(os.path.abspath(__file__))
headers_file = os.path.join(script_dir, '.metagenomongo.csv')
fields = load.load_headers(headers_file)
options = load.load_options(headers_file)

def format_results(results):
    return results


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_csv(filepath):
    df = pd.read_csv(filepath)
    return df

@app.route('/', methods=['GET', 'POST'])
def index():
    # row, column_name, error type
    data = pd.DataFrame()
    results = []
    values = {"default": 0}
    if request.method == 'POST':
        # Handle CSV upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                _, ext = os.path.splitext(file.filename)
                if ext == '.csv':
                    data = pd.read_csv(filepath, dtype=str)  # Load as strings
                elif ext == '.xlsx':
                    data = pd.read_excel(filepath, dtype=str)  # Load as strings
                ####
                df_temp = data
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
                expected_headers = load.load_headers(headers_file)
                
                # Get actual headers from the temporary DataFrame
                imported_headers = list(df_temp.columns)
                
                # Identify headers in the input file that do not appear in the expected headers
                incorrect_headers = [header for header in imported_headers if header not in expected_headers]
                
                if incorrect_headers:

                    result= {"error":"Invalide file structure. Different number of columns or names:::" + ",".join(incorrect_headers)}
                    results.append(result)
                    return render_template('index.html', \
                    fields=fields, values=values, results=results)
                    # # Layout for header correction
                    # suggestion_layout = [
                    #     [sg.Text(f"The following headers from the imported file do not match the expected headers:\n" + "\n".join(incorrect_headers))],
                    #     [sg.Text("Please select the correct header for each mismatched header:")]
                    # ]
                    
                    # Create dropdowns for each incorrect header
                    # for header in incorrect_headers:
                    #     suggestion_layout.append([sg.Text(f"{header}: "), sg.Combo(expected_headers, size=(30, 1), key=f'-{header}-suggestion', readonly=True)])
                    
                    # suggestion_layout.append([sg.Button('Cancel', key='-CANCEL-'), sg.Button('Apply Changes', key='-APPLY-')])
                    
                    # suggestion_popup = sg.Window('Header Suggestions', suggestion_layout, modal=True, keep_on_top=True)
                    # event, values = suggestion_popup.read()
                    # suggestion_popup.close()
                    
                    # if event == '-APPLY-':
                    #     header_mapping = {header: values[f'-{header}-suggestion'] for header in incorrect_headers}
                        
                    #     # Rename the incorrect headers to the selected headers in the DataFrame
                    #     df_temp.rename(columns=header_mapping, inplace=True)
                        
                    #     # Remove duplicate columns if they exist
                    #     df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]
                        
                    #     # Reindex df_temp to match the expected headers, filling missing columns with empty strings
                    #     df_temp = df_temp.reindex(columns=expected_headers, fill_value='')
                        
                    #     # Remove fully empty rows
                    #     df_temp = df_temp[~(df_temp == '').all(axis=1)]
                        
                    #     data = df_temp.values.tolist()
                        
                    #     # Update the table
                    #     window['-TABLE-'].update(values=data, num_rows=50)
                    #     sg.popup('Data imported successfully with header mapping.', title='Import Successful', font=('Arial', 12), keep_on_top=True)
                    # else:
                    #     sg.popup_error('Import cancelled. Please correct the headers manually and try again.', keep_on_top=True)
                else:
                    # No incorrect headers, just update the table
                    df_temp = df_temp.reindex(columns=expected_headers, fill_value='')  # Ensure columns match the expected headers
                    df_temp = df_temp.loc[:, ~df_temp.columns.duplicated()]  # Remove any duplicate columns
                    
                    # Remove fully empty rows
                    df_temp = df_temp[~(df_temp == '').all(axis=1)]
                    
                    data_tolist = df_temp.values.tolist()
                    data = df_temp
                    # Update the table
                    ####
                # elif event == '-CORRECT-':
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
                    result_text = (f'Corrected rows: {corrected_count}\n'
                                f'Number of cells with invalid date: {len(invalid_date_messages)}\n'
                                f'Number of cells with invalid fixed data options: {len(invalid_combobox_messages)}\n'
                                '---\n')
                    
                    # Add detailed errors
                    detailed_errors = '\n'.join(invalid_date_messages + invalid_combobox_messages)
                    result_text += detailed_errors
                    results.append(result_text)

                ###
                return render_template('index.html', \
                    tables=[df_temp.to_html(classes='data', header="true")], \
                    fields=fields, values=values, results=results)
        # Handle manual data entry
        if request.form:
            values = request.form
            result = data_validation.data_type_validation(fields, options, values)
            results.append(result)
            data = pd.DataFrame(result["data"],columns=fields)
            # try:
            #     data = pd.read_csv(pd.compat.StringIO(manual_data))
            #     flash('Data successfully entered and displayed below')
            #     return render_template('index.html', tables=[data.to_html(classes='data', header="true")])
            # except Exception as e:
            #     flash(f'Error in data entry: {e}', 'error')
            #     return redirect(url_for('index'))

    return render_template('index.html', tables=[data.to_html(classes='data', header="true")], fields=fields, results=results, values=values)

if __name__ == '__main__':
    app.run(debug=True)
