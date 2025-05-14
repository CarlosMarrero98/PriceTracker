import requests
import os
from dotenv import load_dotenv

load_dotenv()
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")

def fetch_stock_price(ticker):
    try:
        url = f"https://api.twelvedata.com/quote?symbol={ticker}&apikey={TWELVE_API_KEY}"
        print("🟡 URL:", url)

        response = requests.get(url)
        print("🟢 STATUS:", response.status_code)

        data = response.json()
        print("🔵 RESPONSE:", data)

        if "status" in data and data["status"] == "error":
            return None
        if "close" not in data or data["close"] == "":
            return None

        return {
            "price": round(float(data["close"]), 2),
            "name": data.get("name", "Nombre desconocido")
        }
    except Exception as e:
        print(f"Error al obtener el precio de {ticker}: {e}")
        return None
