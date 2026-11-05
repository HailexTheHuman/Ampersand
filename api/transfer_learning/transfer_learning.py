import json
import requests
import joblib
import s3fs

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
        train_response = requests.post("https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/train_model", json={
            "author_notes_pairs": list(train_author_notes),
            "transfer_learning": True,
            "model_path": "alter-classifiers-672791231237-us-east-1-an/base_classifier"
        })
        if train_response.status_code != 200:
            raise Exception("Training model fetch not implemented")
        # raise NotImplementedError("Training model fetch not implement")
    except Exception as e:
        print(f"error trying to train: {e}")
    test_author_notes = zip(test_authors, test_notes)
    try:
        # f1, score = test_model(model, author_note_pairs=test_author_notes)
        test_response = requests.post("https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/test_model", json={
            "author_note_pairs": list(test_author_notes),
            # "model_path": "alter-classifiers-672791231237-us-east-1-an/models/base_classifier"
            "model": train_response.json().get("model")
        })
        if test_response.status_code != 200:
            raise Exception("Testing model fetch not implemented")
        # raise NotImplementedError("Testing model fetch not implemented")
    except Exception as e:
        print(f"error trying to test: {e}")
    f1 = test_response.json().get("f1")
    score = test_response.json().get("score")
    if f1 > 0.65 and score > 0.65:
        if f1 > old_f1 and score >old_accuracy:
            path = f'alter-classifiers-672791231237-us-east-1-an/base_classifier/{username}'
            # save_model(model, model_path=path)
            fs = s3fs.S3FileSystem()
            fs.makedirs(path, exist_ok=True)
            with fs.open(f"{path}/model.pkl", "wb") as f:
                joblib.dump(model, f)
            # fs.put(f"{path}/model.pkl", f"{path}/model.pkl")
            # raise NotImplementedError("Saving model to database fetch not implemented")
            # save_model_to_database(user_id, path, notes_amount)
            save_response = requests.post("https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/save_model_to_database", json={
                "user_id": user_id,
                "path": path,
                "notes_amount": notes_amount
            })
            if save_response.status_code != 200:
                raise Exception("Saving model to database fetch not implemented")
            # raise NotImplementedError("Saving model to database fetch not implemented")