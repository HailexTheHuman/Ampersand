import os
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
vectorizer = HashingVectorizer()
from pathlib import Path
classifier = SGDClassifier(warm_start=False)
import joblib
import numpy as np
import fastapi
import uvicorn
import psycopg2
import bcrypt

app = fastapi.FastAPI()

def save_model(classifier, vectorizer, model_path):
    # TODO: update the model saving logic for hosted deployment
    joblib.dump(classifier, os.path.join(model_path, 'classifier.pkl'))
    joblib.dump(vectorizer, os.path.join(model_path, 'vectorizer.pkl'))

def load_model(model_path):
    # TODO: update the model loading logic for hosted deployment
    classifier = joblib.load(os.path.join(model_path, 'classifier.pkl'))
    vectorizer = joblib.load(os.path.join(model_path, 'vectorizer.pkl'))
    return classifier, vectorizer


def train_model(training_path=None, transfer_learning=False, model_path=None, author_notes_pairs=None):
    if not training_path and not author_notes_pairs:
        raise ValueError("Either 'training_path' or 'author_notes_pairs' must be provided")
    if transfer_learning and model_path:
        old_classifier, old_vectorizer = load_model(model_path)
        vectorizer = old_vectorizer
    else:
        vectorizer = HashingVectorizer()
        classifier = SGDClassifier(warm_start=False)
    corpus = []
    documents_term_matrixes = []
    authors_per_document = []
    if training_path:
        for file in os.listdir(training_path):
            if (Path(os.path.join(training_path, file))).is_dir():
                for fileName in os.listdir(os.path.join(training_path, file)):
                    with open(os.path.join(training_path, file, fileName), 'r') as f:
                        text = f.read()
                        corpus.append(text.lower())
                        authors_per_document.append(file)
    else:
        for author, text in author_notes_pairs:
            corpus.append(text.lower())
            authors_per_document.append(author)
    documents_term_matrixes = vectorizer.fit_transform(corpus)
    if transfer_learning and model_path:
        classifier = SGDClassifier(warm_start=True)
        old_coef = old_classifier.coef_
        classes = []
        new_class_amount = 0
        for author in authors_per_document:
            if author not in old_classifier.classes_ and author not in classes:
                classes.append(author)
                new_class_amount += 1
        old_intercept = old_classifier.intercept_
        new_intercept = old_intercept
        new_coef = np.concatenate([old_coef, np.zeros((new_class_amount-old_coef.shape[0], old_coef.shape[1]))])
        new_intercept = np.concatenate([new_intercept, np.zeros(new_class_amount-old_intercept.shape[0])])
        classifier.fit(documents_term_matrixes, authors_per_document, coef_init=new_coef, intercept_init=new_intercept)
    else:
        classifier.fit(documents_term_matrixes, authors_per_document)
    predictions = []
    for document in documents_term_matrixes:
        predictions.append(classifier.predict(document)[0])
    f1 = metrics.f1_score(authors_per_document, predictions, average='macro')
    print(f"F1 Score: {f1}")
    score = classifier.score(documents_term_matrixes, authors_per_document)
    print(f"Accuracy: {score}")
    return classifier, vectorizer


def test_model(classifier, vectorizer, testing_path):
    test_corpus = []
    test_authors = []
    test_matrix = []
    for file in os.listdir(testing_path):
        if (Path(os.path.join(testing_path, file))).is_dir():
            for fileName in os.listdir(os.path.join(testing_path, file)):
                with open(os.path.join(testing_path, file, fileName), 'r') as f:
                    text = f.read()
                    test_corpus.append(text.lower())
                    test_authors.append(file)
    test_matrix = vectorizer.transform(test_corpus)
    predictions = []
    for i, document in enumerate(test_corpus):
        X_test = test_matrix[i]
        predicted_author = classifier.predict(X_test)
        predictions.append(predicted_author[0])
    f1 = metrics.f1_score(test_authors, predictions, average='macro')
    print(f"F1 Score: {f1}")
    score = classifier.score(test_matrix, test_authors)
    print(f"Accuracy: {score}")




def encrypt_password(password: str):
    salt = bcrypt.gensalt(10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_user_credentials(username: str, password: str):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="your_database",
            user="your_username",
            password="your_password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0]):
            return True
    except Exception as e:
        print(f"Error checking user credentials: {e}")
    return False

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/predict/")
def create_item(text: str):
    # Process the input text and make a prediction
    # This is a placeholder - replace with actual model prediction logic
    try:
        prediction = "predicted_author"  # Replace with actual prediction
        return fastapi.responses.JSONResponse(status_code=200, content={"prediction": prediction})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/train/")
def train_model(path: str, corpus = None, labels = None):
    if not os.path.exists(path) and (not corpus or not labels):
        return fastapi.responses.JSONResponse(status_code=400, content={"error": "Invalid input"})
    pass

@app.post("/transfer-learning/")
def transfer_learning(corpus: list, labels: list, user_id: int):
    pass

@app.get("/user/{user_id}")
def get_user(user_id: int, username: str, password: str):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="your_database",
            user="your_username",
            password="your_password",
            port="5432"
        )
        cur = conn.cursor()
        if check_user_credentials(username, password):
            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            return fastapi.responses.JSONResponse(status_code=200, content={"user": user})
        else:
            return fastapi.responses.JSONResponse(status_code=401, content={"error": "Invalid credentials"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/note/{user_id}")
def get_notes(user_id: int, author: str):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="your_database",
            user="your_username",
            password="your_password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("SELECT * FROM notes WHERE user_id = %s and author = %s", (user_id, author))
        notes = cur.fetchall()
        return fastapi.responses.JSONResponse(status_code=200, content={"notes": notes})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/note/{user_id}")
def create_note(user_id: int, note: str, author: str):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="your_database",
            user="your_username",
            password="your_password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO notes (user_id, note, author) VALUES (%s, %s, %s)", (user_id, note, author))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Note created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/user/")
def create_user(username: str, email: str, password: str):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="your_database",
            user="your_username",
            password="your_password",
            port="5432"
        )
        cur = conn.cursor()
        encrypted_password = encrypt_password(password)
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, encrypted_password))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "User created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/alter/")
def create_alter(user_id: int, name: str):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="your_database",
            user="your_username",
            password="your_password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute("INSERT INTO alters (user_id, name) VALUES (%s, %s)", (user_id, name))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Alter created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)