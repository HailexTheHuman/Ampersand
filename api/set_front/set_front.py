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




def set_front(event, context):
    body = json.loads(event["body"])
    username = body.get("username")
    alter_name = body.get("alter_name")
    time = body.get("time")
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
        alter_id = None
        cur.execute('SELECT user_id FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user:
            user_id = user[0]
        else:
            return response(404, {"error": "User not found"})
        cur.execute('SELECT alter_id FROM "Alters" WHERE name = %s', (alter_name,))
        alter_result = cur.fetchone()
        if alter_result:
            alter_id = alter_result[0]
        else:
            return response(404, {"error": "Alter not found"})
        cur.execute('SELECT alter_id FROM "Alters" WHERE is_fronting = TRUE and user_id = %s', (user_id,))
        old_alter = cur.fetchall()
        print(f"old alter: {old_alter}")
        # else:
        #     return fastapi.responses.JSONResponse(status_code=404, content={"error": "old Alter not found"})
        
        cur.execute('UPDATE "Alters" SET is_fronting = TRUE WHERE alter_id = %s', (alter_id,))
        conn.commit()
        if old_alter:
            for alt in old_alter:
                cur.execute('UPDATE "FrontHistory" SET end_time = %s WHERE alter_id = %s and end_time is null', (time, alt[0],))
                conn.commit()
                cur.execute('UPDATE "Alters" SET is_fronting = FALSE WHERE is_fronting = TRUE and alter_id =%s', (alt[0],))
                conn.commit()
        cur.execute('INSERT INTO "FrontHistory" (user_id, alter_id, start_time) VALUES (%s, %s, %s)', (user_id, alter_id, time,))
        conn.commit()
        return response(201, {"message": "Alter fronting successfully"})
    except Exception as e:
        return response(500, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()