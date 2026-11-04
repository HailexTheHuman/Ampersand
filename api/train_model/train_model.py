import json
# import os
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
# vectorizer = HashingVectorizer()
# from pathlib import Path
# classifier = SGDClassifier(warm_start=False)
import joblib
import numpy as np

import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }

def save_model(classifier, model_path):
    # TODO: update the model saving logic for hosted deployment
    # joblib.dump(classifier, Path(model_path+'.pkl'))
    pass

def load_model(model_path):
    # TODO: update the model loading logic for hosted deployment
    # classifier = joblib.load(Path(model_path+'.pkl'))
    # return classifier
    pass

def train_model(event, context):
    query_params = event.get('queryStringParameters', {})
    transfer_learning = query_params.get('transfer_learning', False)
    model_path = query_params.get('model_path')
    author_notes_pairs = query_params.get('author_notes_pairs')
    if transfer_learning and model_path:
        old_classifier = load_model(model_path)
    else:
        classifier = SGDClassifier(warm_start=False, loss='modified_huber')
    vectorizer = HashingVectorizer()
    corpus = []
    documents_term_matrixes = []
    authors_per_document = []
    authors = []
    for author, text in author_notes_pairs:
        corpus.append(text.lower())
        authors_per_document.append(author)
    documents_term_matrixes = vectorizer.fit_transform(corpus)
    if transfer_learning and model_path:
        classifier = SGDClassifier(warm_start=True, loss='modified_huber')
        old_coef = old_classifier.coef_
        classes = []
        new_class_amount = 0
        for author in authors_per_document:
            if author not in old_classifier.classes_ and author not in classes:
                classes.append(author)
                new_class_amount += 1
            elif author not in classes:
                classes.append(author)
        old_intercept = old_classifier.intercept_
        new_intercept = old_intercept
        if new_class_amount > 0:
            if new_class_amount > len(old_classifier.classes_):
                new_coef = np.concatenate([old_coef, np.zeros((new_class_amount-old_coef.shape[0], old_coef.shape[1]))])
                new_intercept = np.concatenate([new_intercept, np.zeros(new_class_amount-old_intercept.shape[0])])
                classifier.fit(documents_term_matrixes, authors_per_document, coef_init=new_coef, intercept_init=new_intercept)
            elif new_class_amount == len(old_classifier.classes_) and new_class_amount == len(classes):
                classifier.fit(documents_term_matrixes, authors_per_document, coef_init=old_coef, intercept_init=old_intercept)
            elif new_class_amount < len(old_classifier.classes_):
                new_coef = old_coef[:new_class_amount]
                new_intercept = old_intercept[:new_class_amount]
                classifier.fit(documents_term_matrixes, authors_per_document, coef_init=new_coef, intercept_init=new_intercept)
        elif len(classes) != len(old_classifier.classes_):
            print(f"classes {classes}")
            new_coef = old_coef[:len(classes)]
            new_intercept = old_intercept[:len(classes)]
            classifier.fit(documents_term_matrixes, authors_per_document, coef_init=new_coef, intercept_init=new_intercept)
        else:
            classifier.fit(documents_term_matrixes, authors_per_document, coef_init=old_coef, intercept_init=old_intercept)
    else:
        classifier.fit(documents_term_matrixes, authors_per_document)
    predictions = []
    predictions = classifier.predict(documents_term_matrixes)
    f1 = metrics.f1_score(authors_per_document, predictions, average='macro')
    print(f"F1 Score: {f1}")
    score = classifier.score(documents_term_matrixes, authors_per_document)
    print(f"Accuracy: {score}")
    return classifier