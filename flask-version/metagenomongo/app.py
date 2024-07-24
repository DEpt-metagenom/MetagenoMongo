from flask import Flask, request, render_template, redirect, url_for, flash
import os
import csv
import pandas as pd
from werkzeug.utils import secure_filename

import module.load as load
import module.validation as data_validation

app = Flask(__name__)
app.secret_key = 'supersecretkey'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

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
# print(headers)
# print(options)

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
    result = "result"
    if request.method == 'POST':
        # Handle CSV upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                data = load_csv(filepath)
                flash('File successfully uploaded and displayed below')
                return render_template('index.html', tables=[data.to_html(classes='data', header="true")], fields=fields)
        # Handle manual data entry
        if request.form:
            values = request.form
            print(data_validation.data_type_validation(fields, options, values))
            try:
                data = pd.read_csv(pd.compat.StringIO(manual_data))
                flash('Data successfully entered and displayed below')
                return render_template('index.html', tables=[data.to_html(classes='data', header="true")])
            except Exception as e:
                flash(f'Error in data entry: {e}', 'error')
                return redirect(url_for('index'))

    return render_template('index.html', fields=fields, result=result)

if __name__ == '__main__':
    app.run(debug=True)
