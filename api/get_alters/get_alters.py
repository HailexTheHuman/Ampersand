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
# import bcrypt
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


def get_alters(event, context):
    query_params = event['queryStringParameters']
    username = query_params.get('username')
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
        cur.execute('SELECT name, description, alter_id, is_fronting FROM "Alters" WHERE user_id = %s order by name asc', (user_id,))
        alters_table = cur.fetchall()
        if alters_table is None:
            # return fastapi.responses.JSONResponse(status_code=404, content={"error": "No alters found for the specified user"})
            return response(404, {"error": "No alters found for the specified user"})
        alters = []
        for i in range(len(alters_table)):
            alters.append({"alter":alters_table[i][0], "description":alters_table[i][1], "alter_id":alters_table[i][2], "is_fronting":alters_table[i][3]})
        if alters:
            # return fastapi.responses.JSONResponse(status_code=200, content={"alters": alters})
            return response(200, {"alters": alters})
        else:
            # return fastapi.responses.JSONResponse(status_code=404, content={"error": "No alters found for the specified user"})
            return response(404, {"error": "No alters found for the specified user"})
    except Exception as e:
        # return fastapi.responses.JSONResponse(status_code=500, content={"error": str(e)})
        return response(500, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()