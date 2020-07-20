    import requests

url = "https://eu.mspapis.com/loginidentity/connect/token"

payload = 'client_id=unity.client&client_secret=secret&grant_type=password&scope=openid%20nebula%20offline_access&username=NO%7Cldldld&password=lld&acr_values=gameId%3Aj68d'
headers = {
    'authority': 'eu.mspapis.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'origin': 'https://www.moviestarplanet2.no',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.moviestarplanet2.no/',
    'accept-language': 'nb,no;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
}

response = requests.request("POST", url, headers=headers, data = payload)

refresh_token = response.json()["refresh_token"]

import requests

url = "https://eu.mspapis.com/loginidentity/connect/token"

payload = 'grant_type=refresh_token&refresh_token=' + refresh_token + '&acr_values=gameId%3Aj68d%20profileId%3Aldldld'
headers = {
    'authority': 'eu.mspapis.com',
    'authorization': 'Basic dW5pdHkuY2xpZW50OnNlY3JldA==',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36 Edg/83.0.478.64',
    'content-type': 'application/x-www-form-urlencoded',
    'accept': '*/*',
    'origin': 'https://www.moviestarplanet2.no',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-mode': 'cors',
    'sec-fetch-dest': 'empty',
    'referer': 'https://www.moviestarplanet2.no/',
    'accept-language': 'nb,no;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
}

response = requests.request("POST", url, headers=headers, data = payload)

access_token = response.json()["access_token"]

import requests

url = "https://eu.mspapis.com/profilegreetings/v1/profiles/ldldld/games/j68d/greetings"

payload = "{\r\n    \"greetingType\": \"autograph\",\r\n    \"receiverProfileId\": \"" + booster + "\",\r\n    \"compatibilityMode\": \"Nebula\",\r\n    \"useAltCost\": \"false\"\r\n}"
headers = {
    'Authorization': 'Bearer ' + access_token + '',
    'Content-Type': 'application/json'
}

response = requests.request("POST", url, headers=headers, data = payload)

success = response.json()["result"]

print(' [92m+25[37;1m ' + success + '!')

