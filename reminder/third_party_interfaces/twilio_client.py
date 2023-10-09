from os import environ
from twilio.rest import Client

def send_sms(phone_number: str, message: str):
    account_sid = environ['TWILIO_ACCOUNT_SID']
    auth_token = environ['TWILIO_AUTH_TOKEN']
    client = Client(account_sid, auth_token)

    client.messages.create(
        body=message,
        from_=environ['TWILIO_PHONE_NUMBER'],
        to=phone_number
    )
