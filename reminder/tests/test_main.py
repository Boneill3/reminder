"""
Tests for the main flask module
"""
from unittest.mock import patch, MagicMock, call

from werkzeug.datastructures import ImmutableMultiDict
from assertpy import assert_that

from reminder import main

# pylint: disable=unused-argument
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

client = main.app.test_client()

def test_404():
    response = client.get("/bad_path")
    assert_that(response.status_code).is_equal_to(404)

@patch("reminder.main.id_token")
@patch("reminder.main.Rotation")
def test_send_reminders(rotation:MagicMock, id_token:MagicMock):
    id_token.verify_oauth2_token.return_value = { "aud": "https://localhost/send_reminders",
                                                 "email": "USER@email.com", "email_verified": True}

    response = client.post("/send_reminders",
                           json={"message": { "attributes":
                                             { "collection": "123", "status": "active"}}},
                           headers={"Authorization": "bearer ABC123"})
    rotation.assert_has_calls([call('123', 'active'), call().send_reminder('123')])
    assert_that(response.status_code).is_equal_to(200)

@patch("reminder.main.Rotation")
@patch("reminder.main.RequestValidator")
def test_receive_sms(request_validator:MagicMock, rotation:MagicMock):
    validator = request_validator.return_value
    validator.validate.return_value = True

    from_number = "+11111111111"
    message_body = "blah"
    response = client.post("/receive_sms",
                           data={"From": from_number, "Body": message_body},
                           headers={"X-TWILIO-SIGNATURE": 123})
    request_validator.assert_called_once_with("DEF")
    validator.assert_has_calls([call.validate('https://localhost/receive_sms',
                                              ImmutableMultiDict([("From", from_number),
                                                                  ("Body", message_body)]),
                                              '123')])
    rotation.assert_has_calls([call('trash-reminder'), call().receive('trash-reminder',
                                                                      '+11111111111', 'blah')])
    assert_that(response.status_code).is_equal_to(200)

@patch("reminder.main.Rotation")
@patch("reminder.main.RequestValidator")
def test_receive_invalid_sms(request_validator:MagicMock, rotation:MagicMock):
    validator = request_validator.return_value
    validator.validate.return_value = False
    response = client.post("/receive_sms",
                           data={"from": "123", "Body": "blah"},
                           headers={"X-TWILIO-SIGNATURE": 123})
    assert_that(response.status_code).is_equal_to(401)
    rotation.assert_not_called()
