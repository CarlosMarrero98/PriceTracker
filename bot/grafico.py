import matplotlib.pyplot as plt
from bot.historial import obtener_historial
import io

def generar_grafico(ticker: str) -> io.BytesIO | None:
    precios = obtener_historial(ticker.upper())

    if not precios:
        return None

    fig, ax = plt.subplots()
    ax.plot(precios, marker='o', linestyle='-', color='blue', label=f"{ticker.upper()}")
    ax.set_title(f"Historial de precios - {ticker.upper()}")
    ax.set_xlabel("Registro")
    ax.set_ylabel("Precio (€)")
    ax.grid(True)
    ax.legend()

    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    plt.close(fig)
    buffer.seek(0)
    return buffer
