import re
import string
from nltk.corpus import stopwords

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