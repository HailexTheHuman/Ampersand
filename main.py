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
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_user_credentials(user_id: int, username: str, password: str):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT password FROM "Users" WHERE user_id = %s AND username = %s', (user_id, username))
        user = cur.fetchone()
        print(f"password: {password}")
        print(f"password utf-8: {password.encode('utf-8')}")
        # print(f"user: {user}")
        print(f"actual password: {user[0].strip()}")
        print(f"actual password utf-8: {user[0].strip().encode('utf-8')}")
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].strip().encode('utf-8')):
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


def save_model_to_database(user_id: int, model_path: str):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('INSERT INTO "Models" (user_id, model_path) VALUES (%s, %s)', (user_id, model_path))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Model saved successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/user")
def get_user(user: dict):
    user_id = user.get("user_id")
    username = user.get("username")
    password = user.get("password")
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        if check_user_credentials(user_id, username, password):
            cur.execute('SELECT * FROM "Users" WHERE user_id = %s', (user_id,))
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

@app.get("/notes")
def get_notes(note: dict):
    username = note.get("username")
    author = note.get("author")
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        user_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user and author:
            user_id = user[0]
            alter_id = None
            cur.execute('SELECT alter_id FROM "Alters" WHERE user_id = %s and name = %s', (user_id, author))
            alter = cur.fetchone()
            if not alter:
                return fastapi.responses.JSONResponse(status_code=404, content={"error": "Alter not found"})
            alter_id = alter[0]
            cur.execute('SELECT note FROM "Notes" WHERE alter_id = %s and user_id = %s', (alter_id, user_id))
        elif user and not author:
            user_id = user[0]
            cur.execute('SELECT note, alter_id FROM "Notes" WHERE user_id = %s', (user_id,))
        elif not user:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
        notes_table = cur.fetchall()
        notes = []
        authors = []
        for i in range(len(notes_table)):
            current_author = None
            if not author:
                cur.execute('SELECT name FROM "Alters" WHERE alter_id = %s', (notes_table[i][1],))
                current_author = cur.fetchone()
                if current_author:
                    authors.append(current_author[0])
            else:
                authors.append(author)
            notes.append(notes_table[i][0])
        return fastapi.responses.JSONResponse(status_code=200, content={"notes": notes, "authors": authors})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/note")
def create_note(note: dict):
    username = note.get("username")
    note_text = note.get("note")
    author = note.get("author")
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        user_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
            alter_id = None
            cur.execute('SELECT alter_id FROM "Alters" WHERE user_id = %s and name = %s', (user_id, author))
            alter = cur.fetchone()
            if alter:
                alter_id = alter[0]
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
        if not alter_id:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "Alter not found"})
        cur.execute('INSERT INTO "Notes" (alter_id, note, user_id) VALUES (%s, %s, %s)', (alter_id, note_text, user_id))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Note created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/user")
# def create_user(username: str, email: str, password: str):
def create_user(user: dict):
    username = user.get("username")
    email = user.get("email")
    password = user.get("password")
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        print(f"password: {password}")
        encrypted_password = str(encrypt_password(password).decode('utf-8'))
        print(f"Encrypted password: {encrypted_password}")
        cur.execute('INSERT INTO "Users" (username, email, password) VALUES (%s, %s, %s)', (username, email, encrypted_password))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "User created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e), "username": username, "email": email, "password": password})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/alter")
def create_alter(alter: dict):
    username = alter.get("username")
    alter_name = alter.get("alter_name")
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        user_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
        cur.execute('INSERT INTO "Alters" (user_id, name) VALUES (%s, %s)', (user_id, alter_name))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Alter created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()


@app.get("/alters")
def get_user(user: dict):
    username = user.get("username")
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        user_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
        cur.execute('SELECT name FROM "Alters" WHERE user_id = %s', (user_id,))
        alters_table = cur.fetchall()
        if alters_table is None:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "No alters found for the specified user"})
        alters = []
        for i in range(len(alters_table)):
            alters.append(alters_table[i][0])
        if alters:
            return fastapi.responses.JSONResponse(status_code=200, content={"alters": alters})
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "No alters found for the specified user"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)