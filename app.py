from flask import Flask, render_template, request
from pymysql import connections
from botocore.exceptions import NoCredentialsError, ClientError
import boto3
import os
from config import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

bucket = custombucket
region = customregion

# Connect to the database
db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb
)

output = {}
table = 'employee'


@app.route("/", methods=['GET'])
def index():
    return render_template('index.html')


@app.route("/add_employee", methods=['POST'])
def add_employee():
    empid = request.form['empid']
    fname = request.form['fname']
    lname = request.form['lname']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    image = request.files['image']

    cursor = None

    if image.filename == "":
        return "Please select a file."

    try:
        # Save image locally
        img_filename = f"{empid}_{image.filename}"
        image_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], img_filename)
        image.save(image_path)

        # Upload to S3
        s3 = boto3.client('s3')
        s3.upload_file(image_path, bucket, img_filename)

        # Insert into database
        insert_sql = "INSERT INTO employee (empid, fname, lname, pri_skill, location) VALUES (%s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (empid, fname, lname, pri_skill, location))
        db_conn.commit()

        emp_name = f"{fname} {lname}"
        print("Data inserted into MySQL and image uploaded to S3 successfully.")

        return render_template('success.html', name=emp_name)

    except NoCredentialsError:
        return render_template('error.html', message="Missing AWS credentials.")
    except ClientError as e:
        return render_template('error.html', message="AWS Client Error: " + str(e))
    except Exception as e:
        return render_template('error.html', message="Database/S3 Error: " + str(e))
    finally:
         if cursor:
             cursor.close()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
