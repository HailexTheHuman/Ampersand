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
import psycopg2
import awscrt
import botocore
import boto3
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

def check_model_train_reqs(event, context):
    # user_id, username, last_train_notes_amount, old_f1, old_accuracy
    query_params = event.get("queryStringParameters")
    user_id = query_params.get("user_id")
    username = query_params.get("username")
    last_train_notes_amount = int(query_params.get("last_train_notes_amount"))
    old_f1 = float(query_params.get("old_f1"))
    old_accuracy = float(query_params.get("old_accuracy"))
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
        cur.execute('SELECT COUNT(name) FROM "Alters" WHERE user_id = %s', (user_id,))
        alters = cur.fetchall()
        cur.execute('SELECT COUNT(note_id) FROM "Notes" WHERE user_id = %s', (user_id,))
        note_for_amount = cur.fetchall()
        print(f"alters {alters[0][0]}")
        print(f"note_for_amount {note_for_amount[0][0]}")
        if alters[0][0] >= 2 and ((last_train_notes_amount != 0 and note_for_amount[0][0] >= (last_train_notes_amount*1.5)) or note_for_amount[0][0] % 10 == 0):
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
            # transfer_learning(zip(authors, notes), user_id, username, len(notes), old_f1, old_accuracy)
            raise Exception("Transfer learning fetch not implemented")
    except Exception as e:
        print(f"error checking if we should train {e}")
    finally:
        if conn:
            cur.close()
            conn.close()