import re
import spacy

nlp = spacy.load("en_core_web_sm")
from stop_words import get_stop_words

def remove_punctuation(text):
    text = re.sub(r'[^\w\s]', '', text)
    return text

def to_lowercase(text):
    return text.lower()

def lemmatize_text(text):
    doc = nlp(text)
    lemmatized_text = " ".join([token.lemma_ for token in doc])
    return lemmatized_text

def remove_stopwords(text, language='english'):
    stop_words = get_stop_words(language)
    words = text.split()
    filtered_words = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_words)

def preprocess(text):
    text = remove_punctuation(text)
    text = to_lowercase(text)
    text = lemmatize_text(text)
    text = remove_stopwords(text)
    return text


