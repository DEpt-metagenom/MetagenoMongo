from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename
import io

import module.load as load
import module.validation as data_validation
import module.email as email

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SK')
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
script_dir = os.path.dirname(os.path.abspath(__file__))
headers_file = os.path.join(script_dir, '.metagenomongo.csv')
options = load.load_options(headers_file)
fields = list(options.keys())

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS

@app.route('/change', methods=['POST'])
def change():
    form_data = request.form
    data_list = []
    tmp = []
    count = 0
    for key, value in form_data.items():
        tmp.append(value)
        count += 1
        if count == 86:
            data_list.append(tmp)
            tmp = []
            count = 0
    # return redirect("/")
    results = []
    values = {"default": 0}
    data = pd.DataFrame(data_list, columns=fields)
    data_validation.validation_all( fields, options, results, data)
    return render_template('index_with_table.html', \
                    tables=[data.to_html(classes='data', header="true")], fields=fields, results=results, values=values, df=data)


@app.route('/save', methods=['GET', 'POST'])
def save():
    form_data = request.form
    data_list = []
    tmp = []
    count = 0
    for key, value in form_data.items():
        tmp.append(value)
        count += 1
        if count == 86:
            data_list.append(tmp)
            tmp = []
            count = 0
    df= pd.DataFrame(data_list, columns=fields)
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    output = io.StringIO()
    df.to_csv(output, index=False)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    email.send_email() 
    return send_file(mem, mimetype='text/csv', \
                     as_attachment=True, download_name='metamongo_file.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    # row, column_name, error type
    global fields
    data = pd.DataFrame()
    results = []
    values = {"default": 0}
    if request.method == 'POST':
        # Handle CSV upload
        if 'file' in request.files:
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                _, ext = os.path.splitext(file.filename)
                if ext == '.csv':
                    data = pd.read_csv(filepath, dtype=str)  # Load as strings
                elif ext == '.xlsx':
                    data = pd.read_excel(filepath, dtype=str)  # Load as strings
                df_temp = data
                # Strip whitespace from headers
                df_temp.columns = df_temp.columns.str.strip()
                # Strip whitespace from data
                df_temp = df_temp.applymap(lambda x: x.strip() if isinstance(x, str) else x)
                # Replace NaN with empty strings
                df_temp = df_temp.fillna('')
                # Remove fully empty rows
                df_temp = df_temp[~(df_temp == '').all(axis=1)]
                # Get actual headers from the temporary DataFrame
                imported_fields = list(df_temp.columns)
                # Identify headers in the input file that do not appear in the expected headers
                incorrect_fields = [header for header in imported_fields if header not in fields]
                if incorrect_fields:
                    result= {"error":"Input file contains unexpected fields :::" + ",".join(incorrect_fields)}
                    results.append(result)
                    return render_template('index.html', \
                    fields=fields, values=values, results=results)
                else:
                    # No incorrect headers, just update the table
                    for col in fields:
                        if col not in imported_fields:
                            df_temp[col] = ""
                    fields = [col for col in df_temp]
                    data_validation.validation_all(fields,\
                                    options, results, df_temp)                                
                return render_template('index_with_table.html', \
                    tables=[df_temp.to_html(classes='data', header="true")], \
                    fields=fields, values=values, results=results, df=df_temp)
        # Handle manual data entry
        if request.form:
            fields = list(options.keys())
            values = request.form
            result = data_validation.data_assign(fields, values)
            data = pd.DataFrame(result["data"],columns=fields)
            result.pop("data", None)
            data_validation.validation_all( fields, options, results, data)
            return render_template('index_with_table.html', \
                    tables=[data.to_html(classes='data', header="true")], fields=fields, results=results, values=values, df=data)
    return render_template('index.html', tables=[], fields=fields, results=results, values=values)

if __name__ == '__main__':
    app.run(debug=True)
