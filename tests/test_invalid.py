import requests

routes = ["/coalitions", "/countries"]

base_url = "http://127.0.0.1:5000"

for route in routes:
    r = requests.get(f"{base_url}{route}")
    stc = r.status_code
    if stc == 400:
        print(f"Error while accessing {route}")


