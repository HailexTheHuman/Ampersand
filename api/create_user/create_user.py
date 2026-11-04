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
# import fastapi
# import uvicorn
import psycopg2
import awscrt
import botocore
import boto3
import bcrypt
from cryptography.fernet import Fernet

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

def encrypt_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed



def create_user(event, context):
    event_body = event['body']
    event_body_json = json.loads(event_body)
    username = event_body_json.get("username")
    password = event_body_json.get("password")
    key = Fernet.generate_key()
    try:
        auth_token = boto3.client('rds', region_name='us-east-2').generate_db_auth_token(DBHostname='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com', Port=5432, DBUsername='lambda_user', Region='us-east-2')
        logger.info(f"Generated auth_token: {auth_token}")
        conn = psycopg2.connect(
            host='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com',
            port=5432,
            database='postgres',
            user='lambda_user',
            password=auth_token,
            sslmode='require'
        )
        logger.info(f"Connected to the database: {conn}")
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            return response(409, {"error": f"user {username} already exists"})
        encrypted_password = str(encrypt_password(password).decode('utf-8'))
        cur.execute('INSERT INTO "Users" (username, password, n_key) VALUES (%s, %s, %s)', (username, encrypted_password, key.decode('utf-8')))
        conn.commit()
        return response(201, {"message": "User created successfully"})
    except Exception as e:
        logger.error(f"Error occurred: {e}")
        return response(500, {"error": str(e), "username": username, "password": password})
    finally:
        if conn:
            cur.close()
            conn.close()