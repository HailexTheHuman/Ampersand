import json
# import os
# from sklearn.feature_extraction.text import HashingVectorizer
# from sklearn.linear_model import SGDClassifier
# from sklearn import metrics
# vectorizer = HashingVectorizer()
# from pathlib import Path
# classifier = SGDClassifier(warm_start=False)
# import joblib
# import numpy as np
# import psycopg2
# import awscrt
# import botocore
# import boto3

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

def transfer_learning(event, context):
    # authors_corpus: zip, user_id: int, username: str, notes_amount: int, old_f1: float, old_accuracy: float
    event_body = event['body']
    event_body_json = json.loads(event_body)
    authors_corpus = event_body_json.get("author_corpus")
    user_id = event_body_json.get("user_id")
    username = event_body_json.get("username")
    notes_amount = event_body_json.get("notes_amount")
    old_f1 = event_body_json.get("old_f1")
    old_accuracy = event_body_json.get("old_accuracy")
    print("transfering")
    import random
    test_authors = []
    test_notes = []
    train_authors = []
    train_notes = []
    for author, note in authors_corpus:
        if author not in train_authors:
            train_authors.append(author)
            train_notes.append(note)
        elif random.randint(0, 10) > 7:
            test_authors.append(author)
            test_notes.append(note)
        else:
            train_authors.append(author)
            train_notes.append(note)
    for author in test_authors:
        if author not in train_authors:
            print(f"training data missing author {author}")
    train_author_notes = zip(train_authors, train_notes)
    model = None
    try:
        # model = train_model(author_notes_pairs=train_author_notes, transfer_learning=True, model_path='./models/base_classifier')
        raise NotImplementedError("Training model fetch not implement")
    except Exception as e:
        print(f"error trying to train: {e}")
    test_author_notes = zip(test_authors, test_notes)
    try:
        # f1, score = test_model(model, author_note_pairs=test_author_notes)
        raise NotImplementedError("Testing model fetch not implemented")
    except Exception as e:
        print(f"error trying to test: {e}")
    # if f1 > 0.6 and score > 0.6:
    #     if f1 > old_f1 and score >old_accuracy:
    #         path = f'./models/{username}'
    #         save_model(model, model_path=path)
    #         # save_model_to_database(user_id, path, notes_amount)
    #         raise NotImplementedError("Saving model to database fetch not implemented")