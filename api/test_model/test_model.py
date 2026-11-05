import json
# import os
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
# vectorizer = HashingVectorizer()
# from pathlib import Path
# classifier = SGDClassifier(warm_start=False)
import joblib
# import numpy as np

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


def test_model(event, context):
    # classifier, testing_path=None, author_note_pairs=None
    query_params = event['queryStringParameters']
    author_note_pairs = json.loads(query_params.get('author_note_pairs'))
    classifier = query_params.get('model')
    vectorizer = HashingVectorizer()
    test_corpus = []
    test_authors = []
    test_matrix = []
    authors = []
    if author_note_pairs:
        for author, note in author_note_pairs:
            if author not in authors:
                authors.append(author)
            test_corpus.append(note.lower())
            test_authors.append(author)
    else:
        raise ValueError("Either 'testing_path' or 'author_notes_pairs' must be provided")
    test_matrix = vectorizer.transform(test_corpus)
    predictions = []
    predictions = classifier.predict(test_matrix)
    f1 = metrics.f1_score(test_authors, predictions, average='macro')
    score = classifier.score(test_matrix, test_authors)
    return response(200, {"f1": f1, "score": score})