from test_auth import login, login_session
import credentials
import psycopg2
import os
from dotenv import load_dotenv
from init import BASE_URL
load_dotenv()


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


def test_deletion():
    assert delete_user(credentials.username, credentials.email, login_session) == True

def test_login_after_deletion():
    assert login(login_session) == False