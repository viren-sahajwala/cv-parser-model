from fileinput import filename
import os
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
from models import *
from openpyxl import load_workbook

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'doc'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# splits the filename to obtain the file extension
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return render_template('home.html')


@app.route('/uploads/<name>')
def download_file(name):
    # data extraction code goes here
    resume_text = extract_text_from_file(os.path.join(app.config['UPLOAD_FOLDER'], name),name)
    person_name = extract_names(resume_text)
    contact = extract_phone_number(resume_text)
    email = extract_emails(resume_text)
    skills = extract_skills(resume_text)
    education = extract_education(resume_text)
    
    # appending the candidate data to an existing excel file 
    workbook_name = 'candidates.xlsx'
    wb = load_workbook(workbook_name)
    page = wb.active
    new_candidate = [[person_name, contact, email, skills, education, name]]
    for info in new_candidate:
        page.append(info)
    wb.save(filename=workbook_name)

    return render_template("home.html", person_name = person_name, email = email, contact = contact, skills = skills, education = education, thefilename = name)


if __name__ == "__main__":
    app.run(debug=True)