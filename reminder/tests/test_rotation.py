from reminder import Rotation
from unittest.mock import patch, MagicMock, call
from assertpy import assert_that
from itertools import islice

@patch("reminder.rotation.get_data")
def test_rotation_test(p: MagicMock):
	p.return_value = "123"
	rotation = Rotation()
	assert rotation.rotation_test() == "123"

@patch("reminder.rotation.send_sms")
@patch("reminder.rotation.get_users_by_last_completed_date")
def test_send_reminder_with_no_users_throws_exception(get_users_mock: MagicMock, send_sms_mock:MagicMock):
	get_users_mock.return_value = islice([],0)
	rotation = Rotation()
	assert_that(rotation.send_reminder).raises(KeyError).when_called_with("123")\
    .contains('not found')
	get_users_mock.assert_called()
	send_sms_mock.assert_not_called()

@patch("reminder.rotation.send_sms")
@patch("reminder.rotation.get_users_by_last_completed_date")
def test_send_reminder(get_users_mock: MagicMock, send_sms_mock:MagicMock):
	phone_number = "+12222222222"
	name = "Brian"
	message = f"Hi {name}, it's your turn to take out the trash tonight! Can you pick it up tonight? Please respond with Yes or No." 
	user_record = MagicMock()
	user_record.id = phone_number
	user_record.to_dict.return_value = { "name": name, }
	get_users_mock.return_value = islice([user_record], None)
	rotation = Rotation()
	rotation.send_reminder("123")
	send_sms_mock.assert_called_once_with(phone_number, message)

@patch("reminder.rotation.reminder_is_active")
@patch("reminder.rotation.complete_reminder")
@patch("reminder.rotation.update_user_response")
@patch("reminder.rotation.get_user_by_phone_number")
@patch("reminder.rotation.send_sms")
def test_recieve_positive_response(send_sms:MagicMock, get_user_by_phone_number:MagicMock, update_user_response:MagicMock, complete_reminder:MagicMock, reminder_is_active:MagicMock):
	phone_number = "+5551234567"
	collection = "123"
	message_body = "YES"
	user_record = MagicMock()
	user_record.id = phone_number
	user_record.to_dict.return_value = { "name": "Brian", }
	get_user_by_phone_number.return_value = islice([user_record], None)
	reminder_is_active.return_value = True

	rotation = Rotation()
	rotation.receive(collection, phone_number, message_body)

	send_sms.assert_called_once_with(phone_number, "Got it! Thanks!")
	update_user_response.assert_called_once_with(collection, phone_number, message_body)
	complete_reminder.assert_called_once_with(collection)

@patch("reminder.rotation.get_user_by_phone_number")
def test_recieve_from_non_user(get_user_by_phone_number:MagicMock):
	'''
	This should not happen, because the number should be validated before calling this function
	'''
	get_user_by_phone_number.return_value = islice([],None)

	rotation = Rotation()
	assert_that(rotation.receive).raises(KeyError).when_called_with("123", "123", "blah")\
    .contains('not found')

@patch("reminder.rotation.reminder_is_active")
@patch("reminder.rotation.complete_reminder")
@patch("reminder.rotation.update_user_response")
@patch("reminder.rotation.get_user_by_phone_number")
@patch("reminder.rotation.send_sms")
def test_recieve_non_valid_response(send_sms:MagicMock, get_user_by_phone_number:MagicMock, update_user_response:MagicMock, complete_reminder:MagicMock, reminder_is_active:MagicMock):
	phone_number = "+5551234567"
	collection = "123"
	message_body = "BLAH"
	user_record = MagicMock()
	user_record.id = phone_number
	user_record.to_dict.return_value = { "name": "Brian", }
	get_user_by_phone_number.return_value = islice([user_record], None)
	reminder_is_active.return_value = True

	rotation = Rotation()
	rotation.receive(collection, phone_number, message_body)

	send_sms.assert_called_once_with(phone_number, "I did not understand your response. Please send only yes, no, y or n.")
	update_user_response.assert_not_called()
	complete_reminder.assert_not_called()

@patch("reminder.rotation.reminder_is_active")
@patch("reminder.rotation.complete_reminder")
@patch("reminder.rotation.update_user_response")
@patch("reminder.rotation.get_user_by_phone_number")
@patch("reminder.rotation.send_sms")
def test_recieve_completed_reminder(send_sms:MagicMock, get_user_by_phone_number:MagicMock, update_user_response:MagicMock, complete_reminder:MagicMock, reminder_is_active:MagicMock):
	phone_number = "+5551234567"
	collection = "123"
	message_body = "Yes"
	user_record = MagicMock()
	user_record.id = phone_number
	user_record.to_dict.return_value = { "name": "Brian", }
	get_user_by_phone_number.return_value = islice([user_record], None)
	reminder_is_active.return_value = False

	rotation = Rotation()
	rotation.receive(collection, phone_number, message_body)

	send_sms.assert_called_once_with(phone_number, "Someone already responded, so don't worry about it!")
	update_user_response.assert_not_called()
	complete_reminder.assert_not_called()

@patch("reminder.rotation.get_users_by_last_completed_date")
@patch("reminder.rotation.reminder_is_active")
@patch("reminder.rotation.complete_reminder")
@patch("reminder.rotation.update_user_response")
@patch("reminder.rotation.get_user_by_phone_number")
@patch("reminder.rotation.send_sms")
def test_recieve_negative_response(send_sms:MagicMock, get_user_by_phone_number:MagicMock, update_user_response:MagicMock, complete_reminder:MagicMock, reminder_is_active:MagicMock, get_users_by_last_completed:MagicMock):
	next_message = f"Hi Other, it's your turn to take out the trash tonight! Can you pick it up tonight? Please respond with Yes or No." 
	message = "Got it! Thanks!"
	phone_number = "+5551234567"
	next_phone_number = "+4441234567"
	collection = "123"
	message_body = "No"
	user_record = MagicMock()
	user_record.id = phone_number
	user_record.to_dict.return_value = { "name": "Brian", }
	next_user_record = MagicMock()
	next_user_record.id = next_phone_number
	next_user_record.to_dict.return_value = { "name": "Other", }
	get_user_by_phone_number.return_value = islice([user_record], None)
	reminder_is_active.return_value = True
	get_users_by_last_completed.return_value = islice([next_user_record], None)

	rotation = Rotation()
	rotation.receive(collection, phone_number, message_body)

	send_sms.assert_has_calls([call(phone_number, message), call(next_phone_number, next_message)])
	update_user_response.assert_called_once_with(collection, phone_number ,message_body)
	complete_reminder.assert_not_called()
