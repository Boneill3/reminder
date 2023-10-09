from typing import Generator, Any
from google.cloud import firestore
from google.cloud.firestore import DocumentSnapshot
from google.cloud.firestore_v1.types import WriteResult
from google.cloud.exceptions import NotFound

from datetime import datetime, timedelta

NULL_DATETIME = datetime(1971, 1, 1, 0, 0, 0)

def get_data(name: str):
    return name

def get_users_by_last_completed_date(collection:str, limit:int=None) -> Generator[DocumentSnapshot, Any, None]:
    before_today = datetime.now() - timedelta(days=1)
    db = firestore.Client()
    doc = db.collection(collection).where("last_attempted", "<=", before_today).order_by("last_completed").limit(limit).stream()
    return doc

def get_user_by_phone_number(collection:str, phone_number:str) -> DocumentSnapshot:
    """
    Return user from phone number
    """
    db = firestore.Client()
    doc = db.collection(collection).document(phone_number).get()
    return doc

def update_user_response(collection:str, phone_number:str, message_body:str) -> None:
    db = firestore.Client()
    db.collection(collection).document(phone_number).update({"last_response": message_body})

def complete_reminder(collection:str) -> None:
    db = firestore.Client()
    db.collection("reminders").document(collection).update({"status": "inactive"})

def reminder_is_active(collection: str) -> bool:
    db = firestore.Client()
    reminder = db.collection("reminders").document(collection).get()
    if not reminder.exists:
        raise NotFound("reminder collection not found")

    return reminder.to_dict().get("status") == "active"

def activate_reminder(collection:str) -> None:
    db = firestore.Client()
    db.collection("reminders").document(collection).update({"status": "active"})

# TODO: Change database organization to use embedded collection