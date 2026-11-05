import json
import psycopg2
import awscrt
import botocore
import boto3
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



def can_predict(event, context):
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
        cur.execute('SELECT user_id, last_train_notes_amount, f1, accuracy FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        # https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/check_model_train_reqs
        # check_model_train_reqs(user[0], username, user[1], user[2], user[3])
        response = requests.post("https://z0x5iyn8v6.execute-api.us-east-2.amazonaws.com/Prod/check_model_train_reqs", json={
            "user_id": user[0],
            "username": username,
            "last_train_notes_amount": user[1],
            "f1": user[2],
            "accuracy": user[3]
        })
        if response.status_code != 200:
            raise Exception("Debugging: check_model_train_reqs fetch not implemented")
        cur.execute('SELECT model_path FROM "Users" WHERE username = %s', (username,))
        user = cur.fetchone()
        model_path = user[0]
        print(f"model path: {model_path}")
        if model_path is not None:
            # return fastapi.responses.JSONResponse(status_code=200, content={"can_predict": True})
            return response(200, {"can_predict": True})
        else:
            return response(401, {"error": "model not ready"})
    except Exception as e:
        return response(404, {"error": str(e)})
    finally:
        if conn:
            cur.close()
            conn.close()