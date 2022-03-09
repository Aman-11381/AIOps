import numpy as np
import pandas as pd
import pickle
import string
import re
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer

def read_csv_file(path):
    train_df = pd.read_csv(path)
    train_df = train_df[['Description']]
    return train_df

def extract_words(text):
    return re.sub(r'[^a-zA-Z\s]', '', text)

p = string.punctuation
def remove_punctuation(text):
    return text.translate(str.maketrans('', '', p))

def remove_stopwords(text):
    return ' '.join([word for word in str(text).split() if word not in stopwords.words('english')])

def preprocess(df, col_name):
    df[col_name] = df[col_name].str.lower()
    df[col_name] = df[col_name].apply(lambda text: extract_words(text))
    df[col_name] = df[col_name].apply(lambda text: remove_punctuation(text))
    df[col_name] = df[col_name].apply(lambda text: remove_stopwords(text))
    return df

def vectorize(df, col_name, cv_path):
    cv = pickle.load(open(cv_path,'rb'))
    df_vector = cv.transform(df[col_name])
    return df_vector

def predict_results(df_vector, model_path, le_path):
    lr = pickle.load(open(model_path,'rb'))
    predict = lr.predict(df_vector)
    le = pickle.load(open(le_path, 'rb'))
    predict = le.inverse_transform(predict)
    return predict