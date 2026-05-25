import os
import requests
from datetime import datetime

# =====================================================================
# CONFIGURACIÓN
# =====================================================================
TELEGRAM_TOKEN = "8898046277:AAEtqezJFWbFsTghbCiuWsAbTOLyWSmODvo"
TELEGRAM_CHAT_ID = 8609010281
PRECIO_HISTORICO_FILE = "ultimo_precio.txt"

# ⚠️  PEGA AQUÍ LA URL EXACTA DE TU BÚSQUEDA EN LATAM (copiada del navegador)
URL_VUELO = "https://www.latamairlines.com/cl/es/ofertas-vuelos?origin=SCL&outbound=2026-06-25T00%3A00%3A00.000Z&destination=BSB&adt=1&chd=0&inf=0&trip=RT&cabin=Economy&redemption=false&sort=RECOMMENDED&inbound=2026-06-29T00%3A00%3A00.000Z"

# =====================================================================
# FUNCIONES
# =====================================================================
def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje})
        print("Alerta enviada a Telegram.")
    except Exception as e:
        print(f"Error Telegram: {e}")


def obtener_precio_vuelo():
    from scrapling.fetchers import DynamicFetcher

    if not URL_VUELO:
        print("ERROR: Falta la URL.")
        return None

    print(f"Cargando página (puede tardar 30-60 seg)...")

    try:
        page = DynamicFetcher().fetch(URL_VUELO, headless=True, network_idle=True, timeout=60000)
        print(f"HTTP {page.status} — {page.url}")

        if "/error/" in page.url:
            print("LATAM redirigió a página de error. La URL caducó, genera una nueva desde el navegador.")
            return None

        if page.status >= 400:
            print(f"Error HTTP {page.status}.")
            return None

        selectores = [
            "span[data-testid='flight-card-price']::text",
            ".display-currency-price::text",
            ".price-amount::text",
            "[class*='price']::text",
            "[class*='Price']::text",
            "[class*='fare']::text",
        ]

        for sel in selectores:
            texto = page.css(sel).get()
            if texto and any(c.isdigit() for c in texto):
                print(f"Precio encontrado: '{texto}'")
                digits = "".join(c for c in texto if c.isdigit())
                return int(digits) if digits else None

        print("No se encontró ningún precio.")
        return None

    except Exception as e:
        print(f"Error al cargar: {e}")
        return None


def evaluar_precio(precio_actual):
    if precio_actual is None:
        print("Sin precio. Finalizando.")
        return

    if not os.path.exists(PRECIO_HISTORICO_FILE):
        with open(PRECIO_HISTORICO_FILE, "w") as f:
            f.write(str(precio_actual))
        print(f"Primer registro guardado: ${precio_actual:,} CLP")
        return

    with open(PRECIO_HISTORICO_FILE, "r") as f:
        precio_anterior = int(f.read().strip())

    print(f"Precio anterior: ${precio_anterior:,} CLP")
    print(f"Precio actual:   ${precio_actual:,} CLP")

    with open(PRECIO_HISTORICO_FILE, "w") as f:
        f.write(str(precio_actual))

    if precio_actual < precio_anterior:
        mensaje = (
            f"⚠️ ¡BAJÓ EL VUELO! ✈️\n\n"
            f"• Antes: ${precio_anterior:,} CLP\n"
            f"• Ahora: ${precio_actual:,} CLP\n\n"
            f"Ver aquí:\n{URL_VUELO}"
        )
        enviar_alerta_telegram(mensaje)
    elif precio_actual > precio_anterior:
        print("El precio subió. Sin alerta.")
    else:
        print("Sin cambios en el precio.")


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    print("⚡ Probando Telegram...")
    enviar_alerta_telegram("✈️ Bot activo.")

    print("\n✈️ Rastreando precio...")
    precio = obtener_precio_vuelo()
    evaluar_precio(precio)
    print("Listo.")
