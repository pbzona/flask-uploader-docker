import os
import boto3
from flask import Flask, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './tmp/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

s3 = boto3.resource('s3')
for bucket in s3.buckets.all():
    # Define a unique term to look for in your buckets
    # This is a string in the bucket name (not the entire name itself), and the
    # first result will be used as the bucket to upload to
    if 'upload-photos' in bucket.name:
        bucket_name = bucket.name

def put_in_S3(file, filename):
    data = open(file, 'rb')
    s3.Bucket(bucket_name).put_object(Key=filename, Body=data)
    return redirect(url_for('upload_file'))

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            print('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            path_to_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(path_to_file)
            put_in_S3(path_to_file, filename)
            os.remove(path_to_file)
            return redirect(url_for('upload_file'))
    return render_template('home.html')

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(host='0.0.0.0', debug=True, port=80)
