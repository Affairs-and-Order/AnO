import requests
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

website_url = "http://127.0.0.1:5000"

# Auth test config
username = "test_user123"
email = "affairsandorder@test.com"
password = "testpassword12345"
confirmation = password
key = "testkey12345"
continent = "1"

def delete_user(username, email):
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("DELETE FROM users WHERE username=%s AND email=%s", (username, email))

    return True

def register():

    data = {
        'username': username,
        'email': email,
        'password': password,
        'confirmation': confirmation,
        'key': key,
        'continent': continent
    }

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    delete_user(username, email)

    db.execute("INSERT INTO keys (key) VALUES (%s)", (key,))
    conn.commit()

    response = requests.post(f"{website_url}/signup", data=data, allow_redirects=False)

    try:
        response.headers["set-cookie"]
    except KeyError:
        return False

    try:
        db.execute("SELECT id FROM users WHERE username=%s AND email=%s AND auth_type='normal'", 
        (username, email))
        db.fetchone()[0]
    except:
        return False

    return True

def login():

    data = {
        'username': username,
        'password': password,
        'rememberme': 'on'
    }

    response = requests.post(f"{website_url}/login/", data=data, allow_redirects=False)
    try:
        response.headers["set-cookie"]
    except:
        return False

    return True

def test_register():
    assert register() == True

def test_login():
    assert login() == True