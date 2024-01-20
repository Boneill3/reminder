"""
All database connection tests writted with Mock firestore
"""
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from assertpy import assert_that
from mockfirestore import MockFirestore
from google.cloud.exceptions import NotFound

from reminder.third_party_interfaces import get_users_by_last_completed_date, NULL_DATETIME, \
                                            get_user_by_phone_number, update_user_response, \
                                            complete_reminder, reminder_is_active

# pylint: disable=unused-argument
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=protected-access

@patch("reminder.third_party_interfaces.database.firestore")
def test_get_record_when_no_dates_set_one_record(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+11111111111", {"name": "Brian", "last_completed": NULL_DATETIME,
                              "last_attempted": NULL_DATETIME, "last_response": NULL_DATETIME })
    mock_db._data = {
        "123": {
            brian[0]: brian[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = list(get_users_by_last_completed_date("123", 1))
    assert_that(result).is_length(1)
    assert_that(result[0].id).is_equal_to(brian[0])
    assert_that(result[0].to_dict()).is_equal_to(brian[1])

@patch("reminder.third_party_interfaces.database.firestore")
def test_get_record_when_no_dates_set_two_records(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+11111111111", {"name": "Brian", "last_completed": NULL_DATETIME,
                              "last_attempted": NULL_DATETIME, "last_response": ""})
    annie = ("+12222222222", {"name": "Annie", "last_completed": NULL_DATETIME,
                              "last_attempted": NULL_DATETIME, "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = list(get_users_by_last_completed_date("123", 1))
    assert_that(result).is_length(1)
    assert_that(result[0].id).is_equal_to(brian[0])
    assert_that(result[0].to_dict()).is_equal_to(brian[1])

@patch("reminder.third_party_interfaces.database.firestore")
def test_get_record_when_last_completed_set(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+11111111111", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": NULL_DATETIME, "last_response": ""})
    annie = ("+12222222222", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": NULL_DATETIME, "last_response": ""})
    haley = ("+12345678901", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": NULL_DATETIME, "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = list(get_users_by_last_completed_date("123", 1))
    assert_that(result).is_length(1)
    assert_that(result[0].id).is_equal_to(annie[0])
    assert_that(result[0].to_dict()).is_equal_to(annie[1])

@patch("reminder.third_party_interfaces.database.datetime")
@patch("reminder.third_party_interfaces.database.firestore")
def test_get_record_when_last_attempted_set(firestore_mock: MagicMock, datetime_mock:MagicMock):
    datetime_mock.now.return_value = datetime(2023,2,1)
    datetime_mock.timedelta = timedelta
    mock_db = MockFirestore()
    brian = ("+11111111111", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,1,1), "last_response": ""})
    annie = ("+12222222222", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    haley = ("+12345678901", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = list(get_users_by_last_completed_date("123", 1))
    assert_that(result).is_length(1)
    assert_that(result[0].id).is_equal_to(brian[0])
    assert_that(result[0].to_dict()).is_equal_to(brian[1])

@patch("reminder.third_party_interfaces.database.datetime")
@patch("reminder.third_party_interfaces.database.firestore")
def test_get_record_when_all_attempted(firestore_mock: MagicMock, datetime_mock:MagicMock):
    datetime_mock.now.return_value = datetime(2023,2,1)
    datetime_mock.timedelta = timedelta
    mock_db = MockFirestore()
    brian = ("+11111111111", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    annie = ("+12222222222", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    haley = ("+12345678901", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = list(get_users_by_last_completed_date("123", 1))
    assert_that(result).is_length(0)

@patch("reminder.third_party_interfaces.database.firestore")
def test_get_user_by_phone_number(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+14444444444", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    annie = ("+15555555555", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    haley = ("+16666666666", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = get_user_by_phone_number("123", "+15555555555")
    assert_that(result.id).is_equal_to(annie[0])
    assert_that(result.to_dict()).is_equal_to(annie[1])

@patch("reminder.third_party_interfaces.database.firestore")
def test_get_user_by_phone_number_with_invalid_number(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+14444444444", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    annie = ("+15555555555", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    haley = ("+16666666666", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    result = get_user_by_phone_number("123", "+12222222222")
    assert_that(result.exists).is_false()

@patch("reminder.third_party_interfaces.database.firestore")
def test_update_user_response(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+14444444444", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    annie = ("+15555555555", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    haley = ("+16666666666", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    update_user_response("123", "+15555555555", "Yes")
    assert_that(annie[1].get("last_response")).is_equal_to("Yes")

@patch("reminder.third_party_interfaces.database.firestore")
def test_update_user_response_with_bad_number(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    brian = ("+14444444444", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    annie = ("+15555555555", {"name": "Annie", "last_completed": datetime(2023,1,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    haley = ("+16666666666", {"name": "Haley", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "123": {
            brian[0] : brian[1],
            annie[0] : annie[1],
            haley[0] : haley[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    assert_that(update_user_response).raises(NotFound).when_called_with("123", "+12222222222",
                                                                        "Yes")

@patch("reminder.third_party_interfaces.database.firestore")
def test_complete_reminder(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    rotation = ("123", {"name": "Trash Reminder", "schedule": "0 17 * * THU", "status": "active"})
    brian = ("+14444444444", {"name": "Brian", "last_completed": datetime(2023,2,1),
                              "last_attempted": datetime(2023,2,1), "last_response": ""})
    mock_db._data = {
        "reminders": {
            rotation[0]: rotation[1],
        },
        rotation[0]: {
            brian[0]: brian[1]
        }
    }
    firestore_mock.Client.return_value = mock_db
    complete_reminder(rotation[0], brian[0])
    assert_that(rotation[1].get("status")).is_equal_to("inactive")

@patch("reminder.third_party_interfaces.database.firestore")
def test_is_active(firestore_mock: MagicMock):
    mock_db = MockFirestore()
    rotation = ("123", {"name": "Trash Reminder", "schedule": "0 17 * * THU", "status": "active"})
    other = ("456", {"name": "Other Reminder", "schedule": "0 17 * * THU", "status": "inactive"})
    mock_db._data = {
        "reminders": {
            rotation[0]: rotation[1],
            other[0]: other[1],
        }
    }
    firestore_mock.Client.return_value = mock_db
    assert_that(reminder_is_active("123")).is_true()
    assert_that(reminder_is_active("456")).is_false()
    assert_that(reminder_is_active).raises(NotFound).when_called_with("000")
