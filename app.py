from flask import Flask, redirect, render_template, request, flash, session, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
import os
import scripts.train as train

# specifying the path where the file will be stored in the filesystem
UPLOAD_FOLDER = "static/files"
# set of allowed extensions
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def home():
    return render_template("train_upload.html")

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
            await train_model(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'static/pickle/lr_model.pkl', 'static/pickle/cv.pkl', 'Description', 'Level')
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
            return render_template('result.html')
        return render_template('test_upload.html')

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.debug = True
    app.run()

# function that checks if the extension of the uploaded file is valid or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

async def train_model(file_path, model_path, cv_path, feature_col, label_col):
    train_df = train.read_csv_file(file_path)
    train_df = train.encode_labels(train_df, label_col)
    train_df = train.preprocess(train_df, feature_col)
    y, x_vector = train.vectorize(train_df, feature_col, label_col, cv_path)
    train.train_lr_model(x_vector, y, model_path)