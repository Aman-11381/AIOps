import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer

def read_csv_file(path):
    train_df = pd.read_csv(path)
    train_df = train_df[['Description']]
    return train_df

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

def add_predictions(predictions, file_path):
    test_df_final = pd.read_csv(file_path)
    test_df_final.insert(0, "Level", predictions, True)
    test_df_final.to_csv(file_path, index=False)
