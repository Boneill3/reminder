from werkzeug.datastructures import ImmutableMultiDict
from reminder import main
from assertpy import assert_that
from unittest.mock import patch, MagicMock, call

client = main.app.test_client()

def test_404():
    response = client.get("/bad_path")
    assert_that(response.status_code).is_equal_to(404)

@patch("reminder.main.decode")
@patch("reminder.main.Rotation")
def test_send_reminders(rotation:MagicMock, decode:MagicMock):
    response = client.post("/send_reminders",
                           json={"reminder": "123"},
                           headers={"Authorization": "bearer ABC123"})
    rotation.assert_has_calls([call(), call().send_reminder("123")])
    decode.assert_called_once_with("ABC123")
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
                                              ImmutableMultiDict([("From", from_number), ("Body", message_body)]),
                                              '123')])
    rotation.assert_has_calls([call(), call().receive("trash-reminder", from_number, message_body)])
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
