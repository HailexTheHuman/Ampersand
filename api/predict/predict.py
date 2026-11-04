import json
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
import psycopg2
import awscrt
import botocore
import boto3

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


def predict(event, context):
    body = json.loads(event['body'])
    username = body.get('username')
    text = body.get('note')
    model_path = None
    try:
        auth_token = boto3.client('rds', region_name='us-east-2').generate_db_auth_token(DBHostname='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com', Port=5432, DBUsername='lambda_user', Region='us-east-2')
        conn = psycopg2.connect(
            host='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com',
            port=5432,
            database='postgres',
            user='lambda_user',
            password=auth_token,
            sslmode='require'
        )
        cur = conn.cursor()
        cur.execute('SELECT model_path FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        print(f"user, {user}")
        model_path = user[0]
    except Exception as e:
        return response(500, {"error": str(e)})
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
        print(f"prediction, {predictions}")
        return response(200, {"predictions": predictions, "most_likely": most_likely_prediction[0]})
    except Exception as e:
        return response(500, {"error": str(e)})