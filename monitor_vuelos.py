import os
import requests

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

ORIGEN  = "SCL"
DESTINO = "GIG"
SALIDA  = "2026-06-24"
REGRESO = "2026-06-29"


def generar_urls():
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


def enviar_alerta_telegram(mensaje):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en los secrets.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"}, timeout=10)
        r.raise_for_status()
        print("Mensaje enviado a Telegram.")
    except Exception as e:
        print(f"Error Telegram: {e}")


if __name__ == "__main__":
    latam, sky, despegar, google = generar_urls()

    mensaje = (
        f"✈️ <b>Revisá los vuelos de hoy</b>\n\n"
        f"📍 {ORIGEN} → RIO DE JANEIRO\n"
        f"📅 {SALIDA} → {REGRESO}\n\n"
        f"🔗 <b>Comparar precios:</b>\n"
        f"✈️ <a href='{latam}'>LATAM</a>\n"
        f"✈️ <a href='{sky}'>Sky Airline</a>\n"
        f"🔍 <a href='{despegar}'>Despegar</a>\n"
        f"🔍 <a href='{google}'>Google Flights</a>"
    )

    enviar_alerta_telegram(mensaje)
    print("Listo.")
