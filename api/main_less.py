import os
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn import metrics
vectorizer = HashingVectorizer()
from pathlib import Path
classifier = SGDClassifier(warm_start=False)
import joblib
import numpy as np
import fastapi
import uvicorn
import psycopg2
import awscrt
import botocore
import boto3
import bcrypt
from cryptography.fernet import Fernet
from fastapi.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def save_model(classifier, model_path):
    # TODO: update the model saving logic for hosted deployment
    joblib.dump(classifier, Path(model_path+'.pkl'))

def load_model(model_path):
    # TODO: update the model loading logic for hosted deployment
    classifier = joblib.load(Path(model_path+'.pkl'))
    return classifier









def encrypt_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed

def check_user_credentials(user_id: int, username: str, password: str):
    try:
        # conn = psycopg2.connect(
        #     host="localhost",
        #     database="Ampersand",
        #     user="postgres",
        #     password="password",
        #     port="5432"
        # )
        auth_token = boto3.client('rds', region_name='us-east-2').generate_db_auth_token(DBHostname='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com', Port=5432, DBUsername='postgres', Region='us-east-2')
        conn = psycopg2.connect(
            host='ampersand.cluster-cp86uyi4mruo.us-east-2.rds.amazonaws.com',
            port=5432,
            database='postgres',
            user='postgres',
            password=auth_token,
            sslmode='require'
        )
        cur = conn.cursor()
        cur.execute('SELECT password FROM "Users" WHERE user_id = %s AND username = %s', (user_id, username))
        user = cur.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[0].strip().encode('utf-8')):
            return True
    except Exception as e:
        print(f"Error checking user credentials: {e}")
    return False



