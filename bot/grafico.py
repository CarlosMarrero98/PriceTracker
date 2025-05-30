import io
from datetime import datetime

import matplotlib.pyplot as plt

from bot.db_instance import db


def generar_grafico(chat_id: str, ticker: str) -> io.BytesIO | None:
    historial = db.obtener_historial(chat_id, ticker)

    if not historial:
        return None

    precios = [p for p, _ in historial]
    fechas = [datetime.strptime(f, "%Y-%m-%d %H:%M:%S") for _, f in historial]

    fig, ax = plt.subplots()
    ax.plot(fechas, precios, marker="o", linestyle="-", color="blue", label=f"{ticker.upper()}")  # type: ignore[arg-type]

    ax.set_title(f"Historial de precios - {ticker.upper()}")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Precio ($)")
    ax.grid(True)
    ax.legend()
    fig.autofmt_xdate(rotation=45)

    buffer = io.BytesIO()
    plt.savefig(buffer, format="png")
    plt.close(fig)
    buffer.seek(0)
    return buffer
