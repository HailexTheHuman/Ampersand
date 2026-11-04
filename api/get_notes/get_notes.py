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



def get_notes(event, context):
    query_params = event.get("queryStringParameters")
    author = None
    username = query_params.get("username") if query_params else None
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
        cur.execute('SELECT user_id, n_key FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        if user and author:
            user_id = user[0]
            alter_id = None
            cur.execute('SELECT alter_id FROM "Alters" WHERE user_id = %s and name = %s', (user_id, author))
            alter = cur.fetchone()
            if not alter:
                # return fastapi.responses.JSONResponse(status_code=404, content={"error": "Alter not found"})
                return response(404, {"error": "Alter not found"})
            alter_id = alter[0]
            cur.execute('SELECT note, note_id, to_json(time_posted) FROM "Notes" WHERE alter_id = %s and user_id = %s order by time_posted desc', (alter_id, user_id))
        elif user and not author:
            user_id = user[0]
            cur.execute('SELECT note, alter_id, note_id, to_json(time_posted) FROM "Notes" WHERE user_id = %s order by time_posted desc', (user_id,))
        elif not user:
            return response(404, {"error": "User not found"})
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
        return response(200, {"notes": notes})
    except Exception as e:
        return response(500, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()