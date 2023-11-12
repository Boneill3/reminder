#Set up service-to-service authentication for triggering sending messages
#https://cloud.google.com/run/docs/authenticating/service-to-service

"""
This is the main flask program. Eventually, this should just call
other modules and handle errors only.
"""
from os import environ
from json import loads
import logging

from flask import Flask, request, Response, send_from_directory
from dotenv import load_dotenv
from twilio.request_validator import RequestValidator
from google.auth.exceptions import GoogleAuthError
from google.cloud.logging import Client
from google.oauth2 import id_token
from google.auth.transport import requests

from . import Rotation

app = Flask(__name__)
load_dotenv()

if environ.get("CLOUD_LOGGING", "False") == "True":
    client = Client()
    client.setup_logging()

def authenticate(bearer_token:str, base_url:str) -> bool:
    """
    Authenticate google oauth2 token
    """
    try:
        token = bearer_token.split(" ")[1]

        # Verify and decode the JWT. `verify_oauth2_token` verifies
        claim = id_token.verify_oauth2_token(
            token, requests.Request()
        )

        if claim['aud'] !=  base_url.replace("http://", "https://", 1):
            return False

        if claim['email'] !=  environ.get('PUBSUB_USER') or \
            not claim['email_verified']:
            return False

    except (GoogleAuthError, ValueError):
        return False

    return True

@app.route("/opt-in", methods=["GET"])
def opt_in() -> Response:
    """
    Send opt-in image for 10DL compliance
    """
    return send_from_directory("files", "opt-in.png")

@app.route("/", methods=["GET"])
def test() -> Response:
    """
    Hello World reponse for testing
    """
    return "Hello World"

@app.route("/send_reminders", methods=["POST"])
def send_reminders() -> Response:
    '''
    Call this from pub/sub subscription
    pass reminder key
    '''
    if not authenticate(request.headers.get("Authorization"), request.base_url):
        return "Unauthorized", 401

    payload = loads(request.data.decode("utf-8"))
    message:dict = payload.get("message", {})
    attributes:dict = message.get("attributes", {})

    collection = attributes.get("collection")
    status = attributes.get("status")

    rotation = Rotation(collection, status)
    logging.info("Sending rotation reminders")
    logging.info("Sending rotation: %s", collection)
    rotation.send_reminder(collection)

    logging.warning(request.data.decode("utf-8"))
    # Returning any 2xx status indicates successful receipt of the message.
    return "OK", 200

@app.route("/receive_sms", methods=["POST"])
def receive_sms() -> Response:
    """
    Recieve sms from twilio service
    """
    auth_token = environ['TWILIO_AUTH_TOKEN']
    # url is incorrectly being set to http causing validator to fail
    https_url = f"https{request.url[4:]}"
    validator = RequestValidator(auth_token)
    request_valid = validator.validate(
            https_url,
            request.form,
            request.headers.get('X-TWILIO-SIGNATURE', ''))

    if not request_valid:
        return "Unauthorized", 401

    phone_number = request.form['From']
    message_body = request.form['Body']

    collection = "trash-reminder"

    rotation = Rotation(collection)
    rotation.receive(collection, phone_number, message_body)

    return {}


if __name__ == "__main__":
    debug = environ.get("DEBUG")
    debug = debug == "Yes"
    app.run(debug=debug, host="0.0.0.0", port=int(environ.get("PORT", 5000)))
