import os
import requests
from pathlib import Path

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN",   "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

AMADEUS_KEY    = os.environ.get("AMADEUS_KEY",    "")
AMADEUS_SECRET = os.environ.get("AMADEUS_SECRET", "")

PRECIO_HISTORICO_FILE = Path("ultimo_precio.txt")

ORIGEN  = "SCL"
DESTINO = "GIG"
SALIDA  = "2026-06-24"
REGRESO = "2026-06-29"


def enviar_alerta_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en los secrets.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}, timeout=10)
        r.raise_for_status()
        print("Alerta enviada a Telegram.")
    except Exception as e:
        print(f"Error Telegram: {e}")


def obtener_precio_vuelo():
    if not AMADEUS_KEY or not AMADEUS_SECRET:
        print("ERROR: Faltan AMADEUS_KEY y AMADEUS_SECRET.")
        print("Obtené tus credenciales gratis en: https://developers.amadeus.com")
        return None

    try:
        from amadeus import Client
        amadeus = Client(client_id=AMADEUS_KEY, client_secret=AMADEUS_SECRET)

        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=ORIGEN,
            destinationLocationCode=DESTINO,
            departureDate=SALIDA,
            returnDate=REGRESO,
            adults=1,
            currencyCode="CLP",
            max=5,
        )

        ofertas = response.data
        if not ofertas:
            print("No se encontraron vuelos.")
            return None

        precios = [
            float(o["price"]["grandTotal"])
            for o in ofertas
            if "price" in o and "grandTotal" in o["price"]
        ]

        if not precios:
            print("No se pudo extraer el precio.")
            return None

        precio_min = min(precios)
        print(f"Precio más bajo encontrado: ${precio_min:,.0f} CLP")
        return precio_min

    except Exception as e:
        print(f"Error al consultar Amadeus: {e}")
        return None


def generar_urls_vuelo():
    latam = (
        f"https://www.latam.com/es_cl/apps/personas/booking"
        f"?fecha1_id={SALIDA}&fecha2_id={REGRESO}"
        f"&from_city1={ORIGEN}&to_city1={DESTINO}&auaultos=1&tipo_viaje=RT"
    )
    sky = (
        f"https://www.skyairline.com/vuelos"
        f"?from={ORIGEN}&to={DESTINO}&departureDate={SALIDA}&returnDate={REGRESO}&adults=1"
    )
    despegar = (
        f"https://www.despegar.cl/vuelos/ida-y-vuelta"
        f"/{ORIGEN}/{DESTINO}/{SALIDA}/{REGRESO}/1/0/0/"
    )
    google = (
        f"https://www.google.com/travel/flights?hl=es"
        f"#flt={ORIGEN}.{DESTINO}.{SALIDA}*{DESTINO}.{ORIGEN}.{REGRESO};c:CLP;e:1;sd:1;t:f"
    )
    return latam, sky, despegar, google


def evaluar_precio(precio_actual):
    if precio_actual is None:
        print("Sin precio. Finalizando.")
        return

    try:
        precio_anterior = float(PRECIO_HISTORICO_FILE.read_text().strip())
    except FileNotFoundError:
        PRECIO_HISTORICO_FILE.write_text(str(precio_actual))
        print(f"Primer registro guardado: ${precio_actual:,.0f} CLP")
        return

    print(f"Precio anterior: ${precio_anterior:,.0f} CLP")
    print(f"Precio actual:   ${precio_actual:,.0f} CLP")

    if precio_actual < precio_anterior:
        latam, sky, despegar, google = generar_urls_vuelo()
        mensaje = (
            f"⚠️ ¡BAJÓ EL VUELO! ✈️\n\n"
            f"• Antes: ${precio_anterior:,.0f} CLP\n"
            f"• Ahora: ${precio_actual:,.0f} CLP\n"
            f"• Ruta: {ORIGEN} → RIO ({SALIDA} → {REGRESO})\n\n"
            f"🔗 Reservá ahora:\n"
            f"✈️ LATAM: {latam}\n"
            f"✈️ Sky: {sky}\n"
            f"🔍 Despegar: {despegar}\n"
            f"🔍 Google Flights: {google}"
        )
        enviar_alerta_telegram(mensaje)
    elif precio_actual > precio_anterior:
        print("El precio subió. Sin alerta.")
    else:
        print("Sin cambios en el precio.")

    PRECIO_HISTORICO_FILE.write_text(str(precio_actual))


if __name__ == "__main__":
    print("✈️ Rastreando precio...")
    precio = obtener_precio_vuelo()
    evaluar_precio(precio)
    print("Listo.")

