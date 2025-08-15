# services/start_service.py

from models.user import get_or_create_user

# Set of chat_ids waiting for a file
_awaiting_file = set()


def init_user(chat_id, username=None, first_name=None, last_name=None):
    """
    Ensure user exists in DB and reset awaiting state for this user.
    """
    user = get_or_create_user(
        chat_id=chat_id,
        username=username,
        first_name=first_name,
        last_name=last_name
    )
    _awaiting_file.discard(chat_id)
    return user


def set_awaiting_file(chat_id):
    """Mark that the bot is now waiting for a file from this user."""
    _awaiting_file.add(chat_id)


def clear_awaiting_file(chat_id):
    """Clear the file waiting state for the user."""
    _awaiting_file.discard(chat_id)


def is_awaiting_file(chat_id):
    """Return True if the user is expected to send a file."""
    return chat_id in _awaiting_file
