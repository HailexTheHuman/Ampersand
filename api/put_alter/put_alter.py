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

def put_alter(event, context):
    body = event['body']
    alter = json.loads(body)
    username = alter.get("username")
    old_name = alter.get("old_name")
    new_name = alter.get("new_name")
    description = alter.get("description")
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
        user_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
        else:
            # return fastapi.responses.JSONResponse(status_code=404, content={"error": "User not found"})
            return response(404, {"error": "User not found"})
        if description and new_name:
            cur.execute('UPDATE "Alters" set name = %s, description = %s WHERE user_id = %s and name = %s', (new_name, description, user_id, old_name,))
        elif description:
            cur.execute('UPDATE "Alters" set description = %s WHERE user_id = %s and name = %s', (description, user_id, old_name,))
        else:
            cur.execute('UPDATE "Alters" set name = %s WHERE user_id = %s and name = %s', (new_name, user_id, old_name,))
        conn.commit()
        # return fastapi.responses.JSONResponse(status_code=200, content={"message": "Alter edited successfully"})
        return response(200, {"message": "Alter edited successfully"})
    except Exception as e:
        # return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
        return response(500, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()