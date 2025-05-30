import requests


def fetch_stock_price(symbol: str, api_key: str) -> dict[str, float | str | None]:
    """
    Consulta el precio actual de un activo financiero usando Twelve Data.

    Args:
        symbol (str): Símbolo bursátil del activo (ej. "AAPL").
        api_key (str): Clave de API de Twelve Data.

    Returns:
        Dict[str, Optional[float | str]]: Diccionario con las claves:
            - "precio": precio de cierre del activo (o None si falla).
            - "nombre": nombre de la empresa (o None si falla).
            - "error": mensaje de error (o None si todo fue bien).
    """
    try:
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={api_key}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()

        data = response.json()

        # Validación defensiva
        if "close" not in data or "name" not in data:
            return {
                "precio": None,
                "nombre": None,
                "error": data.get("message", "Respuesta incompleta de la API"),
            }

        precio = float(data["close"])
        nombre_empresa = data["name"]

        return {"precio": precio, "nombre": nombre_empresa, "error": None}

    except (requests.RequestException, TimeoutError, ValueError, KeyError) as e:
        return {"precio": None, "nombre": None, "error": str(e)}
