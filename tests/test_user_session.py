import pytest
from bot import user_session

@pytest.fixture(autouse=True)
def limpiar_sesiones():
    user_session.sessions.clear()

def test_login_y_is_logged_in():
    user_id = 42
    assert not user_session.is_logged_in(user_id)

    user_session.login(user_id)
    assert user_session.is_logged_in(user_id)

def test_logout():
    user_id = 123
    user_session.login(user_id)
    user_session.logout(user_id)

    assert not user_session.is_logged_in(user_id)
