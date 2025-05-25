from bot.mensajes_ayuda import get_commands_text, get_help_text


def test_get_commands_text():
    texto = get_commands_text()
    assert isinstance(texto, str)
    assert "/start" in texto


def test_get_help_text():
    texto = get_help_text()
    assert isinstance(texto, str)
    assert "/seguir" in texto
