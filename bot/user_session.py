sessions = set()

def login(user_id):
    sessions.add(user_id)

def is_logged_in(user_id):
    return user_id in sessions

def logout(user_id):
    sessions.discard(user_id)
