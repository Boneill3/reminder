"""
test_rotation is the test suite for the Rotation class
"""
from unittest.mock import patch, MagicMock, call
from itertools import islice
from assertpy import assert_that
from reminder import Rotation

# pylint: disable=unused-argument
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring

@patch("reminder.rotation.activate_reminder")
class TestRotation:

    def test_rotation_initialization_when_new(self, activate_reminder: MagicMock):
        rotation = Rotation("123", "new")
        assert_that(rotation.collection).is_equal_to("123")
        activate_reminder.assert_called_once_with("123")

    def test_rotation_initialization_when_not_new(self, activate_reminder:MagicMock):
        rotation = Rotation("123", "unknown")
        assert_that(rotation.collection).is_equal_to("123")
        activate_reminder.assert_not_called()

@patch("reminder.rotation.reminder_is_active")
@patch("reminder.rotation.get_users_by_last_completed_date")
@patch("reminder.rotation.get_all_users_by_collection")
@patch("reminder.rotation.send_sms")
@patch("reminder.rotation.update_user_attempted")
class TestSendReminder:

    def test_send_reminder_if_no_available_users_then_message_all(self,
                                                    update_user_attempted:MagicMock,
                                                    send_sms:MagicMock,
                                                    get_all_users_by_collection:MagicMock,
                                                    get_users_by_last_completed:MagicMock,
                                                    reminder_is_active:MagicMock):
        """
        This test ensures that if a key is sent in that does not match a user,
        the proper error is thrown by the application
        """
        get_users_by_last_completed.return_value = islice([],0)
        snapshot = MagicMock()
        snapshot.to_dict.return_value = {"name": "Brian"}
        snapshot.id = "123"
        get_all_users_by_collection.return_value = islice([snapshot], None)

        rotation = Rotation("collection", "unknown")
        rotation.send_reminder("collection")

        get_users_by_last_completed.assert_called()
        send_sms.assert_called_once_with("123", "Hi Brian, NOBODY is able to take out the trash " +
                                         "tonight! 🤷‍♂️ Figure it out, humans!")

    def test_send_reminder(self,
                            update_user_attempted:MagicMock,
                            send_sms:MagicMock,
                            get_all_users_by_collection:MagicMock,
                            get_users_by_last_completed:MagicMock,
                            reminder_is_active:MagicMock):
        """
        This tests the send_reminder function
        """
        phone_number = "+12222222222"
        name = "Brian"
        message = f"Hi {name}, it's your turn to take out the trash tonight! Can you pick" + \
                   " it up tonight? Please respond with Yes or No."
        user_record = MagicMock()
        user_record.id = phone_number
        user_record.to_dict.return_value = { "name": name, }
        get_users_by_last_completed.return_value = islice([user_record], None)

        rotation = Rotation("collection", "unknown")
        rotation.send_reminder("123")

        send_sms.assert_called_once_with(phone_number, message)
        update_user_attempted.assert_called_once_with("123", phone_number)

@patch("reminder.rotation.reminder_is_active")
@patch("reminder.rotation.complete_reminder")
@patch("reminder.rotation.update_user_response")
@patch("reminder.rotation.get_user_by_phone_number")
@patch("reminder.rotation.send_sms")
class TestRecieve:

    def test_recieve_positive_response(self,
                                    send_sms:MagicMock,
                                    get_user_by_phone_number:MagicMock,
                                    update_user_response:MagicMock,
                                    complete_reminder:MagicMock,
                                    reminder_is_active:MagicMock):
        """
        This test verifies that the application responds correctly 
        when it receives a "YES" response.
        """
        phone_number = "+5551234567"
        collection = "123"
        message_body = "YES"
        user_record = MagicMock()
        user_record.exists = True
        get_user_by_phone_number.return_value = user_record
        reminder_is_active.return_value = True

        rotation = Rotation("", "")
        rotation.receive(collection, phone_number, message_body)

        send_sms.assert_called_once_with(phone_number, "Got it! Thanks!")
        update_user_response.assert_called_once_with(collection, phone_number, message_body)
        complete_reminder.assert_called_once_with(collection, phone_number)

    def test_recieve_from_non_user(self,
                                    send_sms:MagicMock,
                                    get_user_by_phone_number:MagicMock,
                                    update_user_response:MagicMock,
                                    complete_reminder:MagicMock,
                                    reminder_is_active:MagicMock):
        '''
        This should not happen, because the number should be validated before calling this function
        '''
        user_record = MagicMock()
        user_record.exists = False
        get_user_by_phone_number.return_value = user_record

        rotation = Rotation("", "")
        assert_that(rotation.receive).raises(KeyError).when_called_with("123", "123", "blah")\
        .contains('not found')

    def test_recieve_non_valid_response(self,
                                    send_sms:MagicMock,
                                    get_user_by_phone_number:MagicMock,
                                    update_user_response:MagicMock,
                                    complete_reminder:MagicMock,
                                    reminder_is_active:MagicMock):
        """
        This tests that the recieve function responds correctly to 
        an invalid response from the user.
        """
        phone_number = "+5551234567"
        collection = "123"
        message_body = "BLAH"
        user_record = MagicMock()
        user_record.exists = True
        get_user_by_phone_number.return_value = user_record
        reminder_is_active.return_value = True

        rotation = Rotation("", "")
        rotation.receive(collection, phone_number, message_body)

        send_sms.assert_called_once_with(phone_number, "I did not understand your response." +
                                         " Please send only yes, no, y or n.")
        update_user_response.assert_not_called()
        complete_reminder.assert_not_called()

    def test_recieve_completed_reminder(self,
                                    send_sms:MagicMock,
                                    get_user_by_phone_number:MagicMock,
                                    update_user_response:MagicMock,
                                    complete_reminder:MagicMock,
                                    reminder_is_active:MagicMock):
        """
        This test makes sure the application responds correctly when
        the recieve function recieves confirmation from the user
        that the task has been completed.
        """
        phone_number = "+5551234567"
        collection = "123"
        message_body = "Yes"
        user_record = MagicMock()
        user_record.exists = True
        get_user_by_phone_number.return_value = user_record
        reminder_is_active.return_value = False

        rotation = Rotation("", "")
        rotation.receive(collection, phone_number, message_body)

        send_sms.assert_called_once_with(phone_number, "Someone already responded, " +
                                         "so don't worry about it!")
        update_user_response.assert_not_called()
        complete_reminder.assert_not_called()

    @patch("reminder.rotation.get_users_by_last_completed_date")
    @patch("reminder.rotation.update_user_attempted")
    def test_recieve_negative_response(self,
                                    update_user_attempted:MagicMock,
                                    get_users_by_last_completed_date:MagicMock,
                                    send_sms:MagicMock,
                                    get_user_by_phone_number:MagicMock,
                                    update_user_response:MagicMock,
                                    complete_reminder:MagicMock,
                                    reminder_is_active:MagicMock):
        """
        This test verifies that the receive function responds correctly when
        it receives a "no" response from the user.
        """
        next_message = "Hi Other, it's your turn to take out the trash tonight! " + \
            "Can you pick it up tonight? Please respond with Yes or No."
        message = "Got it! Thanks!"
        phone_number = "+5551234567"
        next_phone_number = "+4441234567"
        collection = "123"
        message_body = "No"
        user_record = MagicMock()
        user_record.exists = True
        get_user_by_phone_number.return_value = user_record
        next_user_record = MagicMock()
        next_user_record.id = next_phone_number
        next_user_record.to_dict.return_value = { "name": "Other", }
        get_user_by_phone_number.return_value = user_record
        reminder_is_active.return_value = True
        get_users_by_last_completed_date.return_value = islice([next_user_record], None)

        rotation = Rotation("", "")
        rotation.receive(collection, phone_number, message_body)

        send_sms.assert_has_calls([call(phone_number, message),
                                   call(next_phone_number, next_message)])
        update_user_response.assert_called_once_with(collection, phone_number ,message_body)
        update_user_attempted.assert_called_once_with(collection, next_phone_number)
        complete_reminder.assert_not_called()
