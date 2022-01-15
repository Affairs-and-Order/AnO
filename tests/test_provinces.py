from test_auth import login_session
import requests
import psycopg2
import os
from dotenv import load_dotenv
from init import BASE_URL
load_dotenv()

def create_province():
    conn = psycopg2.connect(
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"))

    db = conn.cursor()

    url = f"{BASE_URL}/createprovince"
    data = {
        "name": "test_province"
    }
    r = login_session.post(url, data=data, allow_redirects=True)

    try:
        db.execute("SELECT id FROM provinces WHERE provincename=%s",  (data["name"],))
        result = db.fetchone()[0]
    except:
        return False
    return True

def test_create_province():
    assert create_province() == True