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
from cryptography.fernet import Fernet
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_model(classifier, model_path):
    # TODO: update the model saving logic for hosted deployment
    joblib.dump(classifier, Path(model_path+'.pkl'))
    # joblib.dump(vectorizer, os.path.join(model_path, 'vectorizer.pkl'))

def load_model(model_path):
    # TODO: update the model loading logic for hosted deployment
    classifier = joblib.load(Path(model_path+'.pkl'))
    # vectorizer = joblib.load(os.path.join(model_path, 'vectorizer.pkl'))
    return classifier


def train_model(training_path=None, transfer_learning=False, model_path=None, author_notes_pairs=None):
    if not training_path and not author_notes_pairs:
        raise ValueError("Either 'training_path' or 'author_notes_pairs' must be provided")
    if transfer_learning and model_path:
        old_classifier = load_model(model_path)
    else:
        classifier = SGDClassifier(warm_start=False, loss='modified_huber')
    vectorizer = HashingVectorizer()
    corpus = []
    documents_term_matrixes = []
    authors_per_document = []
    authors = []
    if training_path:
        for file in os.listdir(training_path):
            if (Path(os.path.join(training_path, file))).is_dir():
                authors.append(file)
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
    # print(f"proba stuff: {classifier.predict_proba(documents_term_matrixes)}")
    f1 = metrics.f1_score(authors_per_document, predictions, average='macro')
    print(f"F1 Score: {f1}")
    score = classifier.score(documents_term_matrixes, authors_per_document)
    print(f"Accuracy: {score}")
    # probabilities_arr = classifier.predict_proba(documents_term_matrixes)
    # predictions2 = []
    # for probabilities in probabilities_arr:
    #     probabilities_sort = [probability for probability in probabilities]
    #     probabilities_sort.sort()
    #     curr_max = probabilities_sort[-1]
    #     for index_m in range(len(probabilities)):
    #     #     print(f"curr_argmax {curr_max}")
    #     #     print(f"logits {logits[index_m]}")
    #         if probabilities[index_m] == curr_max:
    #             predictions2.append(authors[index_m])
    #             break
    # f1 = metrics.f1_score(authors_per_document, predictions2, average='macro')
    # print(f"F1 probabilities Score: {f1}")
    return classifier



def test_model(classifier, testing_path=None, author_note_pairs=None):
    vectorizer = HashingVectorizer()
    test_corpus = []
    test_authors = []
    test_matrix = []
    authors = []
    if testing_path:
        for file in os.listdir(testing_path):
            if (Path(os.path.join(testing_path, file))).is_dir():
                authors.append(file)
                for fileName in os.listdir(os.path.join(testing_path, file)):
                    with open(os.path.join(testing_path, file, fileName), 'r') as f:
                        text = f.read()
                        test_corpus.append(text.lower())
                        test_authors.append(file)
    elif author_note_pairs:
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
    print(f"F1 Score: {f1}")
    score = classifier.score(test_matrix, test_authors)
    print(f"Accuracy: {score}")
    return f1, score

def check_model_train_requirements(user_id, username, last_train_notes_amount, old_f1, old_accuracy):
    print("check train reqs")
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT COUNT(name) FROM "Alters" WHERE user_id = %s', (user_id,))
        alters = cur.fetchall()
        cur.execute('SELECT COUNT(note_id) FROM "Notes" WHERE user_id = %s', (user_id,))
        note_for_amount = cur.fetchall()
        print(f"alters {alters[0][0]}")
        print(f"note_for_amount {note_for_amount[0][0]}")
        if alters[0][0] >= 2 and note_for_amount[0][0] >= (last_train_notes_amount*1.5):
            cur.execute('SELECT n_key FROM "Users" WHERE user_id = %s', (user_id,))
            user = cur.fetchone()
            n_key = user[0].encode('utf-8')
            f = Fernet(n_key)
            cur.execute('SELECT N.note, A.name FROM "Notes" as N join "Alters" as A on A.alter_id = N.alter_id WHERE N.user_id = %s', (user_id,))
            notes_table = cur.fetchall()
            notes = []
            authors = []
            for i in range(len(notes_table)):
                authors.append(notes_table[i][1])
                decrypted_note = f.decrypt(notes_table[i][0].encode('utf-8')).decode('utf-8')
                notes.append(decrypted_note)
            transfer_learning(zip(authors, notes), user_id, username, len(notes), old_f1, old_accuracy)
    except Exception as e:
        print(f"error checking if we should train {e}")
    finally:
        if conn:
            cur.close()
            conn.close()


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
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].strip().encode('utf-8')):
            return True
    except Exception as e:
        print(f"Error checking user credentials: {e}")
    return False

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/predict")
def predict(user_text: dict):
    username = user_text.get('username')
    text = user_text.get('note')
    model_path = None
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT model_path FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        print(f"user, {user}")
        model_path = user[0]
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()
    try:
        model = load_model(model_path=model_path)
        print(f"model, {model}")
        print(f"text, {text}")
        vectorizer = HashingVectorizer()
        document_term_matrix = vectorizer.fit_transform([text])
        most_likely_prediction = model.predict(document_term_matrix)
        print(f"most likely, {most_likely_prediction}")
        probabilities = model.predict_proba(document_term_matrix)
        print(f"probabilities, {probabilities}")
        predictions = [{'name':str(model.classes_[i]), 'likelyhood':float(probabilities[0][i])} for i in range(len(model.classes_))]
        # predictions.append({'most_likely':most_likely_prediction[0]})
        print(f"prediction, {predictions}")
        return fastapi.responses.JSONResponse(status_code=200, content={"predictions": predictions, "most_likely": most_likely_prediction[0]})
        # return fastapi.responses.JSONResponse(status_code=200, content={"most_likely": most_likely_prediction})
        # return fastapi.responses.JSONResponse(status_code=200, content=predictions)
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})


# @app.post("/transfer-learning/")
def transfer_learning(authors_corpus: zip, user_id: int, username: str, notes_amount: int, old_f1: float, old_accuracy: float):
    print("transfering")
    import random
    test_authors = []
    test_notes = []
    train_authors = []
    train_notes = []
    for author, note in authors_corpus:
        if random.randint(0, 10) > 7:
            test_authors.append(author)
            test_notes.append(note)
        else:
            train_authors.append(author)
            train_notes.append(note)
    for author in test_authors:
        if author not in train_authors:
            print(f"training data missing author {author}")
    train_author_notes = zip(train_authors, train_notes)
    model = train_model(author_notes_pairs=train_author_notes, transfer_learning=True, model_path='./models/base_classifier')
    test_author_notes = zip(test_authors, test_notes)
    f1, score = test_model(model, author_note_pairs=test_author_notes)
    if f1 > 0.6 and score > 0.6:
        if f1 > old_f1 and score >old_accuracy:
            path = f'./models/{username}'
            save_model(model, model_path=path)
            save_model_to_database(user_id, path, notes_amount)


def save_model_to_database(user_id: int, model_path: str, notes_amount: int):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('UPDATE "Users" SET model_path=%s, last_train_notes_amount=%s WHERE user_id = %s;', (model_path, notes_amount, user_id,))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Model saved successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/canPredict")
def can_predict(username: str):
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT model_path FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        model_path = user[0]
        print(f"model path: {model_path}")
        if model_path is not None:
            return fastapi.responses.JSONResponse(status_code=200, content={"can_predict": True})
        else:
            return fastapi.responses.JSONResponse(status_code=401, content={"error": "model not ready"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=404, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/user")
def get_user(username: str, password: str):
    # user_id = user.get("user_id")
    # username = user.get("username")
    # password = user.get("password")
    print("get /user hit")
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        user_id = user[0]
        if check_user_credentials(user_id, username, password):
            cur.execute('SELECT * FROM "Users" WHERE user_id = %s', (user_id,))
            user = cur.fetchone()
            return fastapi.responses.JSONResponse(status_code=200, content={"user": user})
        else:
            return fastapi.responses.JSONResponse(status_code=401, content={"error": "Invalid credentials"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=404, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/notes")
# def get_notes(username: str, author: str | None):
def get_notes(username: str):
    # username = note.get("username")
    # author = note.get("author")
    # if author == "": author = None
    author = None
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
        cur.execute('SELECT user_id, n_key FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user and author:
            user_id = user[0]
            alter_id = None
            cur.execute('SELECT alter_id FROM "Alters" WHERE user_id = %s and name = %s', (user_id, author))
            alter = cur.fetchone()
            if not alter:
                return fastapi.responses.JSONResponse(status_code=404, content={"error": "Alter not found"})
            alter_id = alter[0]
            cur.execute('SELECT note, note_id, to_json(time_posted) FROM "Notes" WHERE alter_id = %s and user_id = %s', (alter_id, user_id))
        elif user and not author:
            user_id = user[0]
            cur.execute('SELECT note, alter_id, note_id, to_json(time_posted) FROM "Notes" WHERE user_id = %s', (user_id,))
        elif not user:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
        notes_table = cur.fetchall()
        n_key = user[1].encode('utf-8')
        f = Fernet(n_key)
        notes = []
        # authors = []
        for i in range(len(notes_table)):
            current_author = None
            if not author:
                cur.execute('SELECT name FROM "Alters" WHERE alter_id = %s', (notes_table[i][1],))
                current_author = cur.fetchone()
                # if current_author:
                #     authors.append(current_author[0])
            # else:
                # authors.append(author)
            decrypted_note = f.decrypt(notes_table[i][0].encode('utf-8')).decode('utf-8')
            notes.append({ "note":decrypted_note, "author":current_author, "note_id":notes_table[i][2], "time":notes_table[i][3]})
        return fastapi.responses.JSONResponse(status_code=200, content={"notes": notes})
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
    time = note.get("time")
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
        cur.execute('SELECT user_id, n_key, last_train_notes_amount, f1, accuracy FROM "Users" WHERE username = %s', (username,))
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
        n_key = user[1].encode('utf-8')
        f = Fernet(n_key)
        encrypted_note = f.encrypt(note_text.encode('utf-8'))
        cur.execute('INSERT INTO "Notes" (alter_id, note, user_id, time_posted) VALUES (%s, %s, %s, %s)', (alter_id, encrypted_note.decode('utf-8'), user_id, time))
        conn.commit()
        last_train_notes_amount = user[2]
        old_f1 = user[3]
        old_accuracy = user[4]
        check_model_train_requirements(user_id, username, last_train_notes_amount, old_f1, old_accuracy)
        return fastapi.responses.JSONResponse(status_code=201, content={"message": "Note created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.post("/user")
def create_user(user: dict):
    username = user.get("username")
    email = user.get("email")
    password = user.get("password")
    key = Fernet.generate_key()
    try:
        conn = psycopg2.connect(
            host="localhost", #replace with cloud database host when deployed
            database="Ampersand",
            user="postgres",
            password="password",
            port="5432"
        )
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            return fastapi.responses.JSONResponse(status_code=409, content={"message": f"user {username} already exists"})
        encrypted_password = str(encrypt_password(password).decode('utf-8'))
        cur.execute('INSERT INTO "Users" (username, email, password, n_key) VALUES (%s, %s, %s, %s)', (username, email, encrypted_password, key.decode('utf-8')))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=201, content={"message": "User created successfully"})
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
    description = alter.get("description")
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
        if description:
            cur.execute('INSERT INTO "Alters" (user_id, name, description) VALUES (%s, %s, %s)', (user_id, alter_name, description))
        else:
            cur.execute('INSERT INTO "Alters" (user_id, name) VALUES (%s, %s)', (user_id, alter_name))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Alter created successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()


@app.put("/alter")
def edit_alter(alter: dict):
    username = alter.get("username")
    old_name = alter.get("old_name")
    new_name = alter.get("new_name")
    description = alter.get("description")
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
        if description and new_name:
            cur.execute('UPDATE "Alters" set name = %s, description = %s WHERE user_id = %s and name = %s', (new_name, description, user_id, old_name,))
        elif description:
            cur.execute('UPDATE "Alters" set description = %s WHERE user_id = %s and name = %s', (description, user_id, old_name,))
        else:
            cur.execute('UPDATE "Alters" set name = %s WHERE user_id = %s and name = %s', (new_name, user_id, old_name,))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=200, content={"message": "Alter edited successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()


@app.post("/front")
def set_front(alter: dict):
    username = alter.get("username")
    alter_name = alter.get("alter_name")
    time = alter.get("time")
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
        alter_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
        cur.execute('SELECT alter_id FROM "Alters" WHERE name = %s', (alter_name,))
        alter_result = cur.fetchone()
        if alter_result:
            alter_id = alter_result[0]
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "Alter not found"})
        cur.execute('SELECT alter_id FROM "Alters" WHERE is_fronting = TRUE')
        old_alter = cur.fetchone()
        old_alter_id = None
        if old_alter:
            old_alter_id = old_alter[0]
        # else:
        #     return fastapi.responses.JSONResponse(status_code=404, content={"error": "old Alter not found"})
        cur.execute('UPDATE "Alters" SET is_fronting = FALSE WHERE is_fronting = TRUE', )
        conn.commit()
        cur.execute('UPDATE "Alters" SET is_fronting = TRUE WHERE alter_id = %s', (alter_id,))
        conn.commit()
        if old_alter_id:
            cur.execute('UPDATE "FrontHistory" SET end_time = %s WHERE alter_id = %s and end_time is null', (time, old_alter_id,))
            conn.commit()
        cur.execute('INSERT INTO "FrontHistory" (user_id, alter_id, start_time) VALUES (%s, %s, %s)', (user_id, alter_id, time))
        conn.commit()
        return fastapi.responses.JSONResponse(status_code=201, content={"message": "Alter fronting successfully"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/fronthistory")
def get_history(username: str, year: str, month: str, day: str):
    from datetime import date
    today = date(int(year), int(month), int(day))
    # print(f"today is {today}")
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
        cur.execute('SELECT FH.front_id, A.name, to_json(FH.start_time), to_json(FH.end_time) FROM "FrontHistory" as FH join "Alters" as A on FH.alter_id = A.alter_id WHERE FH.user_id = %s and date(FH.end_time) = %s or FH.end_time is null', (user_id,today,))
        history_table = cur.fetchall()
        if history_table is None or len(history_table) < 1:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "No history found for the specified user"})
        fronts = {}
        for i in range(len(history_table)):
            # if fronts[history_table[i][1]] is not None:
            try:
                fronts[history_table[i][1]].append({"front_id":history_table[i][0], "start_time":history_table[i][2], "end_time":history_table[i][3]})
            except Exception:
            # else:
                fronts[history_table[i][1]] = [{"front_id":history_table[i][0], "name":history_table[i][1], "start_time":history_table[i][2], "end_time":history_table[i][3]}]
        if fronts:
            print(f"fronts: {fronts}")
            return fastapi.responses.JSONResponse(status_code=200, content={"fronts": fronts})
        else:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "No alters found for the specified user"})
    except Exception as e:
        return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/alters")
def get_user(username: str):
    # username = user.get("username")
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
        cur.execute('SELECT name, description, alter_id, is_fronting FROM "Alters" WHERE user_id = %s order by name asc', (user_id,))
        alters_table = cur.fetchall()
        if alters_table is None:
            return fastapi.responses.JSONResponse(status_code=404, content={"error": "No alters found for the specified user"})
        alters = []
        for i in range(len(alters_table)):
            alters.append({"alter":alters_table[i][0], "description":alters_table[i][1], "alter_id":alters_table[i][2], "is_fronting":alters_table[i][3]})
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