from unittest.mock import patch, MagicMock, call
from assertpy import assert_that
from reminder.third_party_interfaces import send_sms

@patch("reminder.third_party_interfaces.twilio_client.Client")
def test_send_sms(client:MagicMock):
    from_number = '+19999999999'
    to_number = "+12222222222"
    message = "message"
    send_sms(to_number, message)
    client.assert_has_calls([call('ABC', 'DEF'), call().messages.create(body=message, from_=from_number, to=to_number)])