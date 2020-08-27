import requests

# Login 
# rn it fails for some reason idk why

login_data = {
    "username": "ok",
    "password": "ok"
}

login_response = requests.post("http://127.0.0.1:5000/login", data=login_data)
