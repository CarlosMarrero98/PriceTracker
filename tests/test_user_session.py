from bot.user_session import login, logout, is_logged_in

def test_login_logout():
    user_id = 999
    assert not is_logged_in(user_id)
    login(user_id)
    assert is_logged_in(user_id)
    logout(user_id)
    assert not is_logged_in(user_id)
