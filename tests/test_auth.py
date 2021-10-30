import requests
import psycopg2
import os
from dotenv import load_dotenv
from init import BASE_URL
load_dotenv()

# Auth test config
username = "test_user1234"
email = "affairsandorder@teste.com"
password = "testpassword12345"
confirmation = password
key = "testkey12345"
continent = "1"

login_session = requests.Session()
register_session = requests.Session()

def delete_user(username, email):
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    login_session.post(f"{BASE_URL}/delete_own_account")

    try:
        db.execute("SELECT id FROM users WHERE username=%s AND email=%s AND auth_type='normal'",  (username, email))
        result = db.fetchone()[0]
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

    register_session.post(f"{BASE_URL}/signup", data=data, allow_redirects=True)

    if register_session.cookies.get_dict() == {}:
        return False

    try:
        db.execute("SELECT id FROM users WHERE username=%s AND email=%s AND auth_type='normal'", (username, email))
        result = db.fetchone()[0]
    except:
        return False

    return True

def login():
    data = {
        'username': username,
        'password': password,
        'rememberme': 'on'
    }
    login_session.post(f"{BASE_URL}/login/", data=data, allow_redirects=False)
    return login_session.cookies.get_dict() != {}

def logout():
    base = register_session.cookies.get_dict()
    register_session.get(f"{BASE_URL}/logout")
    return register_session.cookies.get_dict() == {} and base != {}

def test_register():
    assert register() == True

def test_logout():
    assert logout() == True

def test_login():
    assert login() == True

def test_deletion():
    assert delete_user(username, email) == True

def test_login_after_deletion():
    assert login() == False