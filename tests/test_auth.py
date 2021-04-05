import requests
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

website_url = "http://127.0.0.1:5000"

# Auth test config
username = "test_user1234"
email = "affairsandorder@teste.com"
password = "testpassword12345"
confirmation = password
key = "testkey12345"
continent = "1"

s = requests.Session()

def delete_user(username, email):
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    if s.cookies.get_dict() == {}:
        return False

    s.post(f"{website_url}/delete_own_account")

    try:
        db.execute("SELECT id FROM users WHERE username=%s AND email=%s AND auth_type='normal'", 
        (username, email))
        db.fetchone()[0]
    except:
        return True

    return False

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

    db.execute("INSERT INTO keys (key) VALUES (%s)", (key,))
    conn.commit()

    response = s.post(f"{website_url}/signup", data=data, allow_redirects=True)

    print(response.headers)
    print(s.cookies.get_dict())

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

def test_deletion():
    assert delete_user(username, email) == True