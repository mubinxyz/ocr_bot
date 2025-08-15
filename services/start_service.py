# services/start_service.py

from models.user import User
from services.db_service import get_db

def init_user(chat_id, username=None, first_name=None, last_name=None):
    """Ensure user exists in DB. Return user object."""
    with get_db() as db:
        user = db.query(User).filter(User.chat_id == chat_id).first()
        if not user:
            user = User(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                awaiting=False
            )
            db.add(user)
            db.commit()
        return user

def set_awaiting_file(chat_id):
    """Optional: mark that user is expected to send a file."""
    with get_db() as db:
        user = db.query(User).filter(User.chat_id == chat_id).first()
        if user:
            user.awaiting = True
            db.commit()

def clear_awaiting_file(chat_id):
    """Reset the awaiting flag."""
    with get_db() as db:
        user = db.query(User).filter(User.chat_id == chat_id).first()
        if user:
            user.awaiting = False
            db.commit()

def is_awaiting_file(chat_id):
    """Return True if the user is marked as awaiting a file."""
    with get_db() as db:
        user = db.query(User).filter(User.chat_id == chat_id).first()
        return user.awaiting if user else False
