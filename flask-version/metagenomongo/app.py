from flask import Flask, request, render_template, redirect, url_for, send_file
import os
import csv
import pandas as pd
from werkzeug.utils import secure_filename
import re
from datetime import datetime
import io


import module.load as load
import module.validation as data_validation
import module.email as email

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

script_dir = os.path.dirname(os.path.abspath(__file__))
headers_file = os.path.join(script_dir, '.metagenomongo.csv')
fields = load.load_headers(headers_file)
options = load.load_options(headers_file)
# Ensure headers match with .metagenomongo.csv headers
expected_headers = load.load_headers(headers_file)


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_csv(filepath):
    df = pd.read_csv(filepath)
    return df

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
    return send_file(mem, mimetype='text/csv', \
                     as_attachment=True, download_name='metamongo_file.csv')

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

                
                
                # Get actual headers from the temporary DataFrame
                imported_headers = list(df_temp.columns)
                
                # Identify headers in the input file that do not appear in the expected headers
                incorrect_headers = [header for header in imported_headers if header not in expected_headers]
                
                if incorrect_headers:

                    result= {"error":"Invalide file structure. Different number of columns or names:::" + ",".join(incorrect_headers)}
                    results.append(result)
                    return render_template('index.html', \
                    fields=fields, values=values, results=results)
                else:
                    # No incorrect headers, just update the table
                    data_validation.validation_all(expected_headers,\
                                    fields, options, results, df_temp)

                    sender_email = "your_email@gmail.com"
                    sender_password = "your_password"  # Use an app-specific password for better security
                    recipient_email = "recipient@example.com"
                    subject = "Test Email from Python"
                    body = "This is a test email sent from Python!"
                    # email.send_email(sender_email, sender_password, recipient_email, subject, body)                
                return render_template('index.html', \
                    tables=[df_temp.to_html(classes='data', header="true")], \
                    fields=fields, values=values, results=results)
        # Handle manual data entry
        if request.form:
            values = request.form
            result = data_validation.data_type_validation(fields, options, values)
            results.append(result)
            data = pd.DataFrame(result["data"],columns=fields)
            result.pop("data", None)
            data_validation.validation_all(expected_headers, fields, options, results, data)
            return render_template('index.html', tables=[data.to_html(classes='data', header="true")], fields=fields, results=results, values=values)

    return render_template('index.html', tables=[], fields=fields, results=results, values=values)

if __name__ == '__main__':
    app.run(debug=True)
