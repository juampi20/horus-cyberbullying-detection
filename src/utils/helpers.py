import re

import spacy

# Patron para identificar URLs, hasta mal escritas, en un texto. (https://regex101.com/r/sHFkhh/2)
url_pattern = re.compile(
    r'[(http(s)?):\/\/(www\.)?a-zA-Z0-9@:%._\-\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&\/\/=]*)')
# Menciones, RTs (retweets)
clean_pattern = re.compile(r'@\S+|([^A-Za-z \t])|(\w+:\/\/\S+)|^rt')


def preprocess_text(text) -> list:
    nlp = spacy.load('en_core_web_sm')

    text = text.lower()
    text = re.sub(url_pattern, '', text)
    text = re.sub(clean_pattern, '', text)

    doc = nlp(text)
    return [token for token in doc if not token.is_punct and not token.is_space]


def remove_stopwords(tokens) -> list:
    return [token for token in tokens if not token.is_stop]


def lemmatize(tokens) -> list:
    return [token.lemma_ for token in tokens]


def clean_text(text) -> str:
    tokens = preprocess_text(text)
    filtered_tokens = remove_stopwords(tokens)
    lemmatized_tokens = lemmatize(filtered_tokens)
    cleaned_text = ' '.join(lemmatized_tokens)
    return cleaned_text
