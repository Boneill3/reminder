"""
Rotation is a type of reminder that will rotate through a list of
possible people and reminding in order of who completed the task
least recently
"""
from .third_party_interfaces import get_users_by_last_completed_date, send_sms
from .third_party_interfaces import get_user_by_phone_number, update_user_response
from .third_party_interfaces import complete_reminder, reminder_is_active, activate_reminder, \
                                    update_user_attempted, get_all_users_by_collection

class Rotation:
    """
    This class contains the functions necessary for the application to
    rotate between members of a household when sending reminders.
    """
    def __init__(self, collection:str, status:str = None) -> None:
        self.collection = collection

        if status == "new":
            activate_reminder(collection)

    def send_reminder(self, collection: str):
        '''
        Send the reminder to next person on the rotation
        Assumes that the reminder is scheduled to run today and not completed
        '''
        if not reminder_is_active(collection):
            return

        user_record = list(get_users_by_last_completed_date(collection, 1))
        if len(user_record) == 0:
            user_records = get_all_users_by_collection(collection)
            for user in user_records:
                name = user.to_dict().get("name")
                failed_message = f"Hi {name}, NOBODY is able to take out the trash tonight!" + \
                                  " 🤷‍♂️ Figure it out, humans!"
                send_sms(user.id, failed_message)
            return

        phone_number = user_record[0].id
        user = user_record[0].to_dict()

        name = user.get("name")
        message = f"Hi {name}, it's your turn to take out the trash tonight! " + \
                   "Can you pick it up tonight? Please respond with Yes or No."
        send_sms(phone_number, message)
        update_user_attempted(collection, phone_number)

    def receive(self, collection:str, phone_number:str, message_body:str):
        """
        This function processes the response received from the user
        """
        user_record = get_user_by_phone_number(collection, phone_number)
        if not user_record.exists:
            raise KeyError("User not found")

        positive_responses = ["y","yes"]
        negative_responses = ["n", "no"]
        if message_body.lower() not in positive_responses + negative_responses:
            send_sms(phone_number,
                     "I did not understand your response. Please send only yes, no, y or n.")
            return

        if not reminder_is_active(collection):
            send_sms(phone_number, "Someone already responded, so don't worry about it!")
            return

        update_user_response(collection, phone_number, message_body)
        send_sms(phone_number, "Got it! Thanks!")

        if message_body.lower() in positive_responses:
            complete_reminder(collection, phone_number)
        else:
            self.send_reminder(collection)
