import pandas as pd
import pickle
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LogisticRegression

def read_csv_file(path):
    train_df = pd.read_csv(path)
    train_df = train_df[['Level','Description']]
    return train_df

def encode_labels(df, label_col, le_path):
    encoder = LabelEncoder()
    df[label_col] = encoder.fit_transform(df[label_col])
    pickle.dump(encoder, open(le_path, 'wb'))
    return df

def vectorize(df, col_name, label_name, cv_path):
    cv = CountVectorizer()
    df_vector = cv.fit_transform(df[col_name])
    pickle.dump(cv, open(cv_path, 'wb'))
    return df[label_name], df_vector

def train_lr_model(df_vector, y, model_path):
    lr = LogisticRegression()
    lr.fit(df_vector, y)
    pickle.dump(lr, open(model_path, 'wb'))
