#!/usr/bin/env python3
import argparse
import os
import requests
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"


def load_env_file(env_path: Path):
    if not env_path.exists():
        return
    with env_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


load_env_file(ENV_FILE)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

PRECIO_HISTORICO_FILE = BASE_DIR / "ultimo_precio.txt"

ORIGEN  = "SCL"
DESTINO = "GIG"
SALIDA  = "2026-06-24"
REGRESO = "2026-06-29"


def obtener_precio_vuelo():
    try:
        import re
        from fast_flights import FlightData, Passengers, get_flights

        resultado = get_flights(
            flight_data=[
                FlightData(date=SALIDA, from_airport=ORIGEN, to_airport=DESTINO),
                FlightData(date=REGRESO, from_airport=DESTINO, to_airport=ORIGEN),
            ],
            trip="round-trip",
            seat="economy",
            passengers=Passengers(adults=1),
        )

        if not resultado or not resultado.flights:
            print("No se encontraron vuelos.")
            return None

        precios = []
        for f in resultado.flights:
            digits = re.sub(r"[^\d.]", "", str(f.price))
            if digits:
                precios.append(float(digits))

        if not precios:
            print("No se pudo extraer el precio.")
            return None

        precio_min = min(precios)
        print(f"Precio más bajo encontrado: {precio_min:,.0f}")
        return precio_min

    except Exception as e:
        print(f"Error al consultar vuelos: {e}")
        return None


def generar_urls():
    latam = (
        f"https://www.latam.com/es_cl/apps/personas/booking"
        f"?fecha1_id={SALIDA}&fecha2_id={REGRESO}"
        f"&from_city1={ORIGEN}&to_city1={DESTINO}&adultos=1&tipo_viaje=RT"
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
        r = requests.post(
            url,
            json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje, "parse_mode": "HTML"},
            timeout=10,
        )
        r.raise_for_status()
        print("Alerta enviada a Telegram.")
    except Exception as e:
        print(f"Error Telegram: {e}")


def evaluar_precio(precio_actual):
    if precio_actual is None:
        print("Sin precio. Finalizando.")
        return

    try:
        precio_anterior = float(PRECIO_HISTORICO_FILE.read_text().strip())
    except FileNotFoundError:
        PRECIO_HISTORICO_FILE.write_text(str(precio_actual))
        print(f"Primer registro guardado: {precio_actual:,.0f}")
        return

    print(f"Precio anterior: {precio_anterior:,.0f}")
    print(f"Precio actual:   {precio_actual:,.0f}")

    if precio_actual < precio_anterior:
        latam, sky, despegar, google = generar_urls()
        bajada = precio_anterior - precio_actual
        mensaje = (
            f"⚠️ <b>¡BAJÓ EL VUELO!</b> ✈️\n\n"
            f"📍 {ORIGEN} → RIO DE JANEIRO\n"
            f"📅 {SALIDA} → {REGRESO}\n\n"
            f"• Antes: ${precio_anterior:,.0f}\n"
            f"• Ahora: ${precio_actual:,.0f}\n"
            f"• Bajó: ${bajada:,.0f} 🎉\n\n"
            f"🔗 <b>Reservá ahora:</b>\n"
            f"✈️ <a href='{latam}'>LATAM</a>\n"
            f"✈️ <a href='{sky}'>Sky Airline</a>\n"
            f"🔍 <a href='{despegar}'>Despegar</a>\n"
            f"🔍 <a href='{google}'>Google Flights</a>"
        )
        enviar_alerta_telegram(mensaje)
    elif precio_actual > precio_anterior:
        print("El precio subió. Sin alerta.")
    else:
        print("Sin cambios en el precio.")

    PRECIO_HISTORICO_FILE.write_text(str(precio_actual))


def enviar_alerta_prueba():
    mensaje = (
        "✈️ <b>Prueba de alerta de monitor_vuelos</b>\n\n"
        "Este mensaje confirma que la integración con Telegram está funcionando."
    )
    enviar_alerta_telegram(mensaje)


def parse_args():
    parser = argparse.ArgumentParser(description="Monitor de precios de vuelos.")
    parser.add_argument(
        "--test",
        action="store_true",
        help="Enviar una alerta de prueba a Telegram.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.test:
        enviar_alerta_prueba()
    else:
        print("✈️ Rastreando precio...")
        precio = obtener_precio_vuelo()
        evaluar_precio(precio)
        print("Listo.")
