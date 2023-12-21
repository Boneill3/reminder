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
    doc = db.collection(collection).order_by("last_attempted").where("last_attempted", "<=", before_today).order_by("last_completed").limit(limit).stream()
    return doc

def get_user_by_phone_number(collection:str, phone_number:str) -> DocumentSnapshot:
    """
    Return user from phone number
    """
    db = firestore.Client()
    doc = db.collection(collection).document(phone_number).get()
    return doc

def get_all_users_by_collection(collection:str) -> Generator[DocumentSnapshot, Any, None]:
    db = firestore.Client()
    return db.collection(collection).stream()

def update_user_attempted(collection:str, phone_number:str) -> None:
    db = firestore.Client()
    db.collection(collection).document(phone_number).update({"last_attempted": datetime.now()})

def update_user_response(collection:str, phone_number:str, message_body:str) -> None:
    db = firestore.Client()
    db.collection(collection).document(phone_number).update({"last_response": message_body})

def complete_reminder(collection:str, phone_number:str) -> None:
    db = firestore.Client()
    db.collection("reminders").document(collection).update({"status": "inactive"})
    db.collection(collection).document(phone_number).update({"last_completed": datetime.now()})

def reminder_is_active(collection: str) -> bool:
    db = firestore.Client()
    reminder = db.collection("reminders").document(collection).get()
    if not reminder.exists:
        raise NotFound(f"reminder collection {collection} not found")

    return reminder.to_dict().get("status") == "active"

def activate_reminder(collection:str) -> None:
    db = firestore.Client()
    db.collection("reminders").document(collection).update({"status": "active"})

# TODO: Change database organization to use embedded collection