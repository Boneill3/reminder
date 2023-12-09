from os import environ
from google.auth.jwt import decode
from google.oauth2 import id_token
from google.auth.transport import requests

def authenticate(bearer_token:str, base_url:str) -> bool:
    try:
        token = bearer_token.split(" ")[1]

        # replace with decode?

        # Verify and decode the JWT. `verify_oauth2_token` verifies
        claim = id_token.verify_oauth2_token(
            token, requests.Request()
        )

        if claim['aud'] !=  base_url.replace("http://", "https://", 1):
            return False

        if claim['email'] !=  environ.get('PUBSUB_USER') or \
            not claim['email_verified']:
            return False

    except Exception:
        return False
    
    return True