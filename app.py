from flask import Flask, render_template, request, redirect
from pymysql import connections

import boto3
import os
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

app.config['UPLOAD_FOLDER'] = 'uploads'

s3 = boto3.client('s3')

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)
output = {}
table = 'employee'





@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_employee', methods=['POST'])
def add_employee():
    empid = request.form['empid']
    fname = request.form['fname']
    lname = request.form['lname']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    image = request.files['image']

    if image:
        img_filename = f"{empid}_{image.filename}"
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], img_filename))
        s3.upload_file(os.path.join(app.config['UPLOAD_FOLDER'], img_filename), custombucket, img_filename)

    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO employee (empid, fname, lname, pri_skill, location) VALUES (%s, %s, %s, %s, %s)",
                   (empid, fname, lname, pri_skill, location))
    db_conn.commit()
    cursor.close()

    return redirect('/')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

