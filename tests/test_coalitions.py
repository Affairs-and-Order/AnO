from test_auth import login_session
import requests
import psycopg2
import os
from dotenv import load_dotenv
from init import BASE_URL
load_dotenv()

coalition_type = "Open"
coalition_name = "test_coalition"
coalition_desc = "Coalition for testing"

def establish_coalition():
    data = {
        "type": coalition_type,
        "name": coalition_name,
        "description": coalition_desc
    }
    login_session.post(f"{BASE_URL}/establish_coalition", data=data, allow_redirects=True)

    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    try:
        db.execute("SELECT * FROM colNames WHERE name=%s AND description=%s AND type=%s",  (coalition_name, coalition_desc, coalition_type))
        result = db.fetchone()[0]
    except:
        return False

    return True


def test_establish_coalition():
    assert establish_coalition() == True