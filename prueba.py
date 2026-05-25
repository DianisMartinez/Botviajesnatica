import requests
from scrapling import Scrapler

# === CONFIGURACIÓN DE PRUEBA ===
TELEGRAM_TOKEN = "8898046277:AAEtqezJFWbFsTghbCiuWsAbTOLyWSmODvo"
TELEGRAM_CHAT_ID = 8609010281 # Tu ID de usuario (número)

def probar_telegram():
    print("🔹 Probando envío a Telegram...")
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": "¡Hola! Tu Codespace ya se comunica con Telegram ✈️"}
    res = requests.post(url, json=payload)
    if res.status_code == 200:
        print("✅ ¡Mensaje de Telegram recibido con éxito!")
    else:
        print(f"❌ Error en Telegram. Código de respuesta: {res.status_code}")

def probar_scrapling():
    print("\n🔹 Probando Scrapling en la nube...")
    try:
        scrapler = Scrapler(webdriver_mode="playwright")
        # Vamos a intentar abrir una página simple y segura para probar
        page = scrapler.get("https://example.com")
        titulo = page.text("h1")
        print(f"✅ Scrapling funcionó. Título capturado: '{titulo}'")
    except Exception as e:
        print(f"❌ Error con Scrapling: {e}")

if __name__ == "__main__":
    probar_telegram()
    probar_scrapling()