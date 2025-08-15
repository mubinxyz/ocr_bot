# services/start_service.py

from models.user import get_or_create_user

# Tracks which users are expected to send files
# Key: chat_id, Value: True if awaiting file
awaiting_file = {}


def init_user(chat_id, username=None, first_name=None, last_name=None):
    """
    Ensure user exists in DB and set awaiting_file state to False.
    """
    user = get_or_create_user(
        chat_id=chat_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    awaiting_file[chat_id] = False
    return user


def set_awaiting_file(chat_id):
    """
    Mark that the bot is now waiting for a file from this user.
    """
    awaiting_file[chat_id] = True


def reset_awaiting_file(chat_id):
    """
    Reset the file waiting state for the user.
    """
    awaiting_file[chat_id] = False


def is_awaiting_file(chat_id):
    """
    Returns True if the user is expected to send a file.
    """
    return awaiting_file.get(chat_id, False)
