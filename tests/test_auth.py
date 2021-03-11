import requests
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()

website_url = "http://127.0.0.1:5000"

def register():

    username = "test_user123"
    email = "affairsandorder@test.com"
    password = "testpassword12345"
    confirmation = password
    key = "testkey12345"
    continent = "1"

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

    login_url = website_url + "/signup"
    response = requests.post(login_url, data=data, allow_redirects=False)
    try:
        response.headers["set-cookie"]
        return True
    except KeyError:
        return False

def test_register():
    assert register() == True