#Set up service-to-service authentication for triggering sending messages
#https://cloud.google.com/run/docs/authenticating/service-to-service

"""
This is the main flask program. Eventually, this should just call
other modules and handle errors only.
"""
from os import environ
from flask import Flask, request, Response
from dotenv import load_dotenv
from reminder import Rotation
from twilio.request_validator import RequestValidator
from google.auth.jwt import decode
from google.auth.exceptions import InvalidValue, MalformedError

app = Flask(__name__)
load_dotenv()

@app.route("/send_reminders", methods=["POST"])
def send_reminders() -> Response:
    '''
    Call this from pub/sub subscription
    pass reminder key
    '''
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        return "Unauthorized", 401

    # split the auth type and value from the header.
    auth_type, creds = auth_header.split(" ", 1)
    if auth_type.lower() != "bearer":
        return "Unauthorized", 401

    try:
        decode(creds)
    except (InvalidValue, MalformedError):
        return "Unauthorized", 401

    reminder = request.json.get("reminder")
    rotation = Rotation()
    rotation.send_reminder(reminder)
    return {}

@app.route("/receive_sms", methods=["POST"])
def receive_sms() -> Response:
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

    # TODO: Can we get collection from From or To?
    # For now hardcode to single collection
    collection = "trash-reminder"

    rotation = Rotation()
    rotation.receive(collection, phone_number, message_body)
    
    return {}


if __name__ == "__main__":
    debug = environ.get("DEBUG")
    debug = debug == "Yes"
    app.run(debug=debug, host="0.0.0.0", port=int(environ.get("PORT", 5000)))