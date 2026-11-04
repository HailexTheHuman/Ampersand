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
# from cryptography.fernet import Fernet

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

def check_user_credentials(user_id: int, username: str, password: str):
    conn = None
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
        cur.execute('SELECT password FROM "Users" WHERE user_id = %s AND username = %s', (user_id, username))
        user = cur.fetchone()
        logger.info(f"Fetched user from database: {user}")
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].strip().encode('utf-8')):
            return True
    except Exception as e:
        logger.error(f"Error checking user credentials: {e}")
        raise e
    finally:
        if conn:
            cur.close()
            conn.close()
    return False

def get_user(event, context):
    query_params = event['queryStringParameters']
    username = query_params.get('username')
    password = query_params.get('password')
    logger.info(f"Query parameters: {query_params}")
    logger.info(f"Fetching user with username: {username}")
    logger.info(f"Password provided: {password}")
    # event_body = event['body']
    # event_body_json = json.loads(event_body)
    # username = event_body_json.get("username")
    # password = event_body_json.get("password")
    
    conn = None
    try:
        auth_token = boto3.client('rds', region_name='us-east-2').generate_db_auth_token(DBHostname='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com', Port=5432, DBUsername='lambda_user', Region='us-east-2')
        # auth_token = ""
        conn = psycopg2.connect(
            host='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com',
            port=5432,
            database='postgres',
            user='lambda_user',
            password=auth_token,
            sslmode='require'
        )
        cur = conn.cursor()
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        logger.info(f"Fetched user_id from database: {user}")
        user_id = user[0]
        logger.info(f"User ID to be used for credential check: {user_id}")
        if check_user_credentials(user_id, username, password):
        # if False:
            cur.execute('SELECT * FROM "Users" WHERE user_id = %s', (user_id,))
            user = cur.fetchone()
            return response(200, {"user": user})
        else:
            return response(401, {"error": "Invalid credentials"})
    except Exception as e:
        logger.error(f"Error fetching user: {e}")
        return response(404, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()
