import requests
import os
from dotenv import load_dotenv

load_dotenv()
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

def fetch_stock_price(ticker):
    try:
        url = f"https://api.twelvedata.com/quote?symbol={ticker}&apikey={TWELVE_API_KEY}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # Validación explícita si hay error
        if "status" in data and data["status"] == "error":
            return None
        if "price" not in data or data["price"] == "":
            return None

        return {
            "price": round(float(data["price"]), 2),
            "name": data.get("name", "Nombre desconocido")
        }
    except Exception as e:
        print(f"Error al obtener el precio de {ticker}: {e}")
        return None

