import json
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
import psycopg2
import awscrt
import botocore
import joblib
from s3fs import S3FileSystem as fs
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
        model_path = user[0]
    except Exception as e:
        return response(500, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()
    try:
        model = None
        with fs().open(f"{model_path}/model.pkl", "rb") as f:
            model = joblib.load(f)
        vectorizer = HashingVectorizer()
        document_term_matrix = vectorizer.fit_transform([text])
        most_likely_prediction = model.predict(document_term_matrix)
        probabilities = model.predict_proba(document_term_matrix)
        predictions = [{'name':str(model.classes_[i]), 'likelyhood':float(probabilities[0][i])} for i in range(len(model.classes_))]
        return response(200, {"predictions": predictions, "most_likely": most_likely_prediction[0]})
        # return response(200, {"predictions": [], "most_likely": None})
    except Exception as e:
        return response(500, {"error": str(e)})