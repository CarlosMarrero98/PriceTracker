import pytest
from bot.telegram_bot import start, login_cmd, logout_cmd
from bot import user_session

@pytest.mark.asyncio
async def test_start_no_logueado():
    class FakeMessage:
        async def reply_text(self, text):
            self.text = text

    class FakeUser:
        id = 1
        first_name = "Alejandro"

    class FakeUpdate:
        effective_user = FakeUser()
        message = FakeMessage()

    class FakeContext:
        args = []

    update = FakeUpdate()
    context = FakeContext()

    # Asegurar que no está logueado
    user_session.sessions.clear()
    await start(update, context)

    assert "¡Hola Alejandro" in update.message.text
    assert "usa /login" in update.message.text

@pytest.mark.asyncio
async def test_login_y_logout():
    class FakeMessage:
        async def reply_text(self, text):
            self.text = text

    class FakeUser:
        id = 42

    class FakeUpdate:
        effective_user = FakeUser()
        message = FakeMessage()

    class FakeContext:
        args = []

    update = FakeUpdate()
    context = FakeContext()

    await login_cmd(update, context)
    assert user_session.is_logged_in(update.effective_user.id)
    assert "✅ Sesión iniciada" in update.message.text

    await logout_cmd(update, context)
    assert not user_session.is_logged_in(update.effective_user.id)
    assert "🔒 Sesión cerrada" in update.message.text
