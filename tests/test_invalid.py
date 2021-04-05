import requests
from init import BASE_URL, main_session

def invalid():
    routes = ["/coalitions", "/countries", "/provinces"]
    for route in routes:
        r = requests.get(f"{BASE_URL}{route}")
        stc = r.status_code
        if stc == 400:
            return route
    return False

def test_invalid():
    assert invalid() == False