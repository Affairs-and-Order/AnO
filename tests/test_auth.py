import requests
import psycopg2
import os
from dotenv import load_dotenv
from init import BASE_URL
import credentials
load_dotenv()

login_session = requests.Session()
register_session = requests.Session()

def delete_user(username, email, session):
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    session.post(f"{BASE_URL}/delete_own_account")

    try:
        db.execute("SELECT id FROM users WHERE username=%s AND email=%s AND auth_type='normal'",  (username, email))
        result = db.fetchone()[0]
    except:
        return True
    return False

def register(session):
    data = {
        'username': credentials.username,
        'email': credentials.email,
        'password': credentials.password,
        'confirmation': credentials.confirmation,
        'key': credentials.key,
        'continent': credentials.continent
    }

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    db.execute("INSERT INTO keys (key) VALUES (%s)", (credentials.key,))
    conn.commit()

    session.post(f"{BASE_URL}/signup", data=data, allow_redirects=True)

    if session.cookies.get_dict() == {}:
        return False

    try:
        db.execute("SELECT id FROM users WHERE username=%s AND email=%s AND auth_type='normal'", (credentials.username, credentials.email))
        result = db.fetchone()[0]
    except:
        return False

    return True

def login(session):
    data = {
        'username': credentials.username,
        'password': credentials.password,
        'rememberme': 'on'
    }
    session.post(f"{BASE_URL}/login/", data=data, allow_redirects=False)
    return session.cookies.get_dict() != {}

def logout(session):
    base = session.cookies.get_dict()
    session.get(f"{BASE_URL}/logout")
    return session.cookies.get_dict() == {} and base != {}

def test_register():
    assert register(register_session) == True

def test_logout():
    assert logout(register_session) == True

def test_login():
    assert login(login_session) == True
