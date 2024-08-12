from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import pandas as pd
from werkzeug.utils import secure_filename
import io

import module.load as load
import module.validation as data_validation
import module.email as email

app = Flask(__name__)
secret_key = os.getenv('FLASK_SK')
if not secret_key:
    raise ValueError("FLASK_SK environment variable is not set")
app.secret_key = secret_key
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

@app.route('/save', methods=['GET', 'POST'])
def save():
    csv_data = request.form['csv_data']
    df = pd.read_html(csv_data, index_col=None)[0]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    output = io.StringIO()
    df.to_csv(output, index=False)
    mem = io.BytesIO()
    mem.write(output.getvalue().encode('utf-8'))
    mem.seek(0)
    email.send_email() 
    return send_file(mem, mimetype='text/csv', \
                     as_attachment=True, download_name='metamongo_file.csv')

@app.route('/correct', methods=['GET', 'POST'])
def correct():
    results = []
    values = {"default": 0}
    values = request.form
    csv_data = request.form['csv_data']
    data = pd.read_html(csv_data, index_col=None)[0]
    data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
    data = data.fillna("")
    data = data.astype(str)
    data_validation.validation_all(fields, options, results, data)
    return render_template('index.html', tables=[data.to_html(classes='data', header="true")], fields=fields, results=results, values=values)

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
                imported_headers = list(df_temp.columns)
                # Identify headers in the input file that do not appear in the expected headers
                incorrect_headers = [header for header in imported_headers if header not in fields]
                if incorrect_headers:
                    result= {"error":"Input file contains unexpected fields :::" + ",".join(incorrect_headers)}
                    results.append(result)
                    return render_template('index.html', \
                    fields=fields, values=values, results=results)
                else:
                    # No incorrect headers, just update the table
                    data_validation.validation_all(fields,\
                                    options, results, df_temp)                                
                return render_template('index.html', \
                    tables=[df_temp.to_html(classes='data', header="true")], \
                    fields=fields, values=values, results=results)
        # Handle manual data entry
        if request.form:
            values = request.form
            result = data_validation.data_assign(fields, values)
            data = pd.DataFrame(result["data"],columns=fields)
            result.pop("data", None)
            data_validation.validation_all( fields, options, results, data)
            return render_template('index.html', tables=[data.to_html(classes='data', header="true")], fields=fields, results=results, values=values)
    return render_template('index.html', tables=[], fields=fields, results=results, values=values)

if __name__ == '__main__':
    app.run(debug=True)
