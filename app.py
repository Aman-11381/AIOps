from flask import Flask, redirect, render_template, request, flash, send_from_directory, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import scripts.train as train
import scripts.predict as pred

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
    return render_template("train_upload.html")

# **************************PREDICT ROUTE - SERVES TEST DATA UPLOAD FORM****************************
@app.route('/predict')
def predict():
    return render_template('test_upload.html')

@app.route("/upload_train", methods=["POST"])
async def upload_train():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No File Part.")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            flash("File uploaded successfully")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            await train_model(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'Level', 'static/pickle/le.pkl')
            return redirect( url_for('predict'))
        return render_template('train_upload.html')

@app.route('/upload_test',methods=['POST'])
async def upload_test():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("No File Part.")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("No selected file")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            flash("File uploaded successfully")
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            predictions = await predict_results(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'static/pickle/le.pkl')
            print(predictions)
            # return render_template('result.html')
            return redirect(url_for('download'))
        return render_template('test_upload.html')
    
@app.route('/download')
def download():
    return send_from_directory(app.config["UPLOAD_FOLDER"], 'log_test.csv')

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
    train_df = train.preprocess(train_df, feature_col)
    y, x_vector = train.vectorize(train_df, feature_col, label_col, cv_path)
    train.train_lr_model(x_vector, y, model_path)

# asynchronous function to load the count vectorizer, model and use them to predict the results
async def predict_results(file_path, model_path, cv_path, feature_col, le_path):
    test_df = pred.read_csv_file(file_path)
    test_df = pred.preprocess(test_df, feature_col)
    test_df_vector = pred.vectorize(test_df, feature_col, cv_path)
    predictions = pred.predict_results(test_df_vector, model_path, le_path)
    pred.add_predictions(predictions, file_path)
    return predictions