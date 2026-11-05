import json
import psycopg2
import awscrt
import botocore
import boto3
from cryptography.fernet import Fernet
import requests

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



def create_note(event, context):
    body = json.loads(event['body'])
    username = body.get("username")
    note_text = body.get("note")
    author = body.get("author")
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
            return response(404, {"error": "User not found"})
        if not alter_id:
            return response(404, {"error": "Alter not found"})
        n_key = user[1].encode('utf-8')
        f = Fernet(n_key)
        encrypted_note = f.encrypt(note_text.encode('utf-8'))
        cur.execute('INSERT INTO "Notes" (alter_id, note, user_id, time_posted) VALUES (%s, %s, %s, %s)', (alter_id, encrypted_note.decode('utf-8'), user_id, time))
        conn.commit()
        last_train_notes_amount = user[2]
        old_f1 = user[3]
        old_accuracy = user[4]
        # check_model_train_requirements(user_id, username, last_train_notes_amount, old_f1, old_accuracy)
        response_checked = requests.post("https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/check_model_train_reqs", json={
            "user_id": user_id,
            "username": username,
            "last_train_notes_amount": last_train_notes_amount,
            "old_f1": old_f1,
            "old_accuracy": old_accuracy
        })
        if response_checked.status_code != 200:
            raise Exception("Check model train requirements fetch not implemented")
        # return response(201, {"message": "Note created successfully"})
    except Exception as e:
        return response(500, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()