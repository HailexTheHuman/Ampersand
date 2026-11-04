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




def get_history(event, context):
    # username: str, year: str, month: str, day: str
    query_params = event['queryStringParameters']
    username = query_params.get('username')
    year = query_params.get('year')
    month = query_params.get('month')
    day = query_params.get('day')
    try:
        from datetime import date
        print(f"year {year} month {month} day {day}")
        today = date(int(year), int(month), int(day))
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
        cur.execute('SELECT FH.front_id, A.name, to_json(FH.start_time), to_json(FH.end_time) FROM "FrontHistory" as FH join "Alters" as A on FH.alter_id = A.alter_id WHERE FH.user_id = %s and (date(FH.end_time) = %s or FH.end_time is null or date(FH.start_time) = %s or (date(FH.end_time) > %s and date(FH.start_time) < %s))', (user_id,today,today,today,today))
        history_table = cur.fetchall()
        if history_table is None or len(history_table) < 1:
            # return fastapi.responses.JSONResponse(status_code=404, content={"error": "No history found for the specified user"})
            return response(404, {"error": "No history found for the specified user"})
        fronts = {}
        for i in range(len(history_table)):
            # if fronts[history_table[i][1]] is not None:
            try:
                fronts[history_table[i][1]].append({"front_id":history_table[i][0], "start_time":history_table[i][2], "end_time":history_table[i][3]})
            except Exception:
            # else:
                fronts[history_table[i][1]] = [{"front_id":history_table[i][0], "name":history_table[i][1], "start_time":history_table[i][2], "end_time":history_table[i][3]}]
        if fronts:
            print(f"fronts: {fronts}")
            # return fastapi.responses.JSONResponse(status_code=200, content={"fronts": fronts})
            return response(200, {"fronts": fronts})
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