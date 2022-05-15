from flask import Flask, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import scripts.train as train
import scripts.predict as pred
import scripts.preprocess as preprocess
import pandas as pd
import json
import csv

# specifying the path where the file will be stored in the filesystem
UPLOAD_FOLDER = "static/files"
# set of allowed extensions
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


# **************************HOME ROUTE - SERVES TRAINING DATA UPLOAD FORM*****************************
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/upload_train", methods=["GET", "POST"])
async def upload_train():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print(type(file))
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            csv_to_json(os.path.join(app.config["UPLOAD_FOLDER"], filename), "train.json")
            return redirect(url_for('train_preview', filename=filename))
        return render_template('train_upload.html')
    return redirect(url_for('home'))

@app.route('/train_preview/<filename>')
def train_preview(filename):
    return render_template('train_preview.html', filename=filename)

@app.route('/training', methods=['GET','POST'])
async def training():
    if(request.method == 'POST'):
        filename = request.form['filename']
        await train_model(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'Level', 'static/pickle/le.pkl')
    return redirect( url_for('predict'))

# **************************PREDICT ROUTE - SERVES TEST DATA UPLOAD FORM****************************
@app.route('/predict')
def predict():
    return render_template('test_upload.html')


@app.route('/upload_test', methods=['GET','POST'])
async def upload_test():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            csv_to_json(os.path.join(app.config["UPLOAD_FOLDER"], filename), "test.json")
            return redirect(url_for('test_preview', filename=filename))
        return render_template('test_upload.html')
    return redirect('predict')

@app.route('/test_preview/<filename>')
def test_preview(filename):
    test_data = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    return render_template('test_preview.html', filename=filename)

@app.route('/predicting', methods=['POST'])
async def predicting():
    if(request.method == 'POST'):
        filename = request.form['filename']
        await predict_results(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'static/pickle/le.pkl')
        result = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        csv_to_json(os.path.join(app.config["UPLOAD_FOLDER"], filename), "result.json")

        return render_template('result_preview.html', filename=filename)
 
@app.route('/download', methods=['POST'])
def download():
    filename = request.form['filename']
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.debug = True
    app.run()

# function that checks if the extension of the uploaded file is valid or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# asynchronous function to preprocess the training data, train the model and save the model
async def train_model(file_path, model_path, cv_path, feature_col, label_col, le_path):
    train_df = train.read_csv_file(file_path)
    train_df = train.encode_labels(train_df, label_col, le_path)
    train_df = preprocess.preprocess(train_df, feature_col)
    y, x_vector = train.vectorize(train_df, feature_col, label_col, cv_path)
    train.train_lr_model(x_vector, y, model_path)

# asynchronous function to load the count vectorizer, model and use them to predict the results
async def predict_results(file_path, model_path, cv_path, feature_col, le_path):
    test_df = pred.read_csv_file(file_path)
    test_df = preprocess.preprocess(test_df, feature_col)
    test_df_vector = pred.vectorize(test_df, feature_col, cv_path)
    predictions = pred.predict_results(test_df_vector, model_path, le_path)
    pred.add_predictions(predictions, file_path)

def csv_to_json(csv_file_path, json_file_name):

    json_file_path = os.path.join(app.config["UPLOAD_FOLDER"], json_file_name) 

    data={}
    with open(csv_file_path) as csv_file:
        data["data"] = []
        csv_reader = csv.DictReader(csv_file)
        for rows in csv_reader:
            data["data"].append(rows)
    
    with open(json_file_path, 'w') as json_file:
        json_file.write(json.dumps(data, indent=4))

# *******************************REST API******************************************

@app.route("/upload", methods=["POST"])
async def upload():

    if request.method == 'POST':

        # return a bad request if the request does not contain a file part
        if 'file' not in request.files:
            return jsonify({
                'message': 'No file part in the request.'
            }), 400

        # return bad request if no file was selected by the user before submitting the request
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'message': 'No file selected.'
            }), 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            csv_to_json(os.path.join(app.config["UPLOAD_FOLDER"], filename), "train.json")
            return jsonify({
                'message': 'File uploaded successfully.',
                'upload_folder': app.config['UPLOAD_FOLDER'],
                'json_filename': 'train.json',
                'csv_filename': filename
            }), 200
            
        return jsonify({
            'message': 'Some unexpected error occurred.'
        }), 400


@app.route("/train_classifier", methods=["POST"])
async def train_classifier():

    if(request.method == 'POST'):

        filename = request.form['train_csv_filename']

        # return bad request if the file does not exist
        if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename)) == False:
            return jsonify({
                'message': 'The file does not exist.'
            }), 400

        await train_model(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'Level', 'static/pickle/le.pkl')

        # return request successful when the model training is complete
        return jsonify({
            'message': 'Model Training Successful'
        }), 200

@app.route("/generate_results", methods=["POST"])
async def generate_results():

    if(request.method == 'POST'):
        
        filename = request.form['test_csv_filename']

        # return bad request if the file does not exist
        if os.path.exists(os.path.join(app.config["UPLOAD_FOLDER"], filename)) == False:
            return jsonify({
                'message': 'The file does not exist.'
            }), 400

        await predict_results(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'static/pickle/le.pkl')

        result = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        csv_to_json(os.path.join(app.config["UPLOAD_FOLDER"], filename), "result.json")

        return jsonify({
            'message': 'Results Generation Successful',
            'upload_folder': app.config['UPLOAD_FOLDER'],
            'json_filename': 'result.json',
            'csv_filename': filename
        }), 200        