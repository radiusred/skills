import jwt
import time
import requests

def get_gh_app_token(client_id, private_key, installation_id):
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": client_id,
    }
    encoded_jwt = jwt.encode(payload, private_key, algorithm="RS256")

    headers = {
        "Authorization": f"Bearer {encoded_jwt}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]
