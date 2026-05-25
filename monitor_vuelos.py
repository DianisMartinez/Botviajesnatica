import os
import requests
from datetime import datetime
from scrapling import Fetcher

# =====================================================================
# 1. CONFIGURACIÓN INICIAL
# =====================================================================

# Credenciales de Telegram ya integradas
TELEGRAM_TOKEN = "8898046277:AAEtqezJFWbFsTghbCiuWsAbTOLyWSmODvo"
TELEGRAM_CHAT_ID = 8609010281

# Archivo histórico local
PRECIO_HISTORICO_FILE = "ultimo_precio.txt"

# URL de ejemplo para vuelos LATAM (Osorno ZOS a Santiago SCL)
# NOTA: Asegúrate de pegar tu link completo de búsqueda aquí si el actual está recortado
URL_VUELO = "https://www.latamairlines.com/cl/es/vuelos-resultados?from=ZOS&to=SCL"


# =====================================================================
# 2. FUNCIONES DEL SCRIPT
# =====================================================================

def enviar_alerta_telegram(mensaje):
    """Se conecta con la API de Telegram para enviar un mensaje de texto"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensaje
    }
    try:
        requests.post(url, json=payload)
        print("¡Alerta enviada con éxito a tu Telegram!")
    except Exception as e:
        print(f"Error crítico al intentar enviar la alerta de Telegram: {e}")


def obtener_precio_vuelo():
    """Abre el navegador con Playwright, espera la carga de datos y extrae la tarifa más baja"""
    # Iniciamos Fetcher en modo playwright para entornos en la nube (Codespaces)
    scrapler = Fetcher(auto_match=True, webdriver_mode="playwright") 
    
    print("Abriendo el navegador invisible y cargando la página de vuelos...")
    page = scrapler.get(URL_VUELO)
    
    # Damos 10 segundos para que la interfaz de LATAM cargue completamente las ofertas de vuelos
    print("Esperando a que terminen de cargar las tarifas en la pantalla...")
    page.wait(10) 
    
    try:
        # === SELECTOR REAL PARA LATAM ===
        # Las páginas de LATAM suelen agrupar los montos numéricos principales bajo la clase '.display-curreny-price'
        # o contenedores con la estructura de texto del valor. Usamos este selector adaptado:
        texto_precio = page.text(".display-curreny-price, span[data-testid='flight-card-price'], .price-amount")
        
        if not texto_precio:
            print("Alerta: No se encontró el precio. La página sigue cargando o cambió el selector de clase.")
            return None
            
        print(f"Texto bruto capturado de la web: '{texto_precio}'")
        
        # === LIMPIEZA DE DATOS ===
        # Extrae únicamente los dígitos numéricos descartando el símbolo '$', los puntos y letras de divisa
        precio_limpio = "".join(filter(str.isdigit, texto_precio))
        
        if not precio_limpio:
            return None
            
        return int(precio_limpio)
        
    except Exception as e:
        print(f"Ocurrió un error inesperado al intentar extraer el precio: {e}")
        return None


def evaluar_precio(precio_actual):
    """Compara la tarifa actual contra el récord previo guardado localmente"""
    if precio_actual is None:
        print("Cancelando evaluación de precio debido a que la captura falló.")
        return

    # Si es la primera ejecución, inicializa el archivo de texto histórico
    if not os.path.exists(PRECIO_HISTORICO_FILE):
        with open(PRECIO_HISTORICO_FILE, "w") as f:
            f.write(str(precio_actual))
        print(f"Primer registro completado. Base guardada: ${precio_actual:,} CLP.")
        return

    # Carga el valor almacenado anteriormente
    with open(PRECIO_HISTORICO_FILE, "r") as f:
        precio_anterior = int(f.read().strip())

    print(f"-> Registro Histórico: ${precio_anterior:,} CLP")
    print(f"-> Captura de Hoy:     ${precio_actual:,} CLP")

    # Si la tarifa bajó respecto al histórico, dispara la notificación
    if precio_actual < precio_anterior:
        mensaje = (
            f"⚠️ ¡BAJÓ EL VUELO! ✈️\n\n"
            f"Buenas noticias, el pasaje bajó de precio:\n"
            f"• Antes: ${precio_anterior:,} CLP\n"
            f"• Ahora: ${precio_actual:,} CLP\n\n"
            f"Aprovecha de revisar aquí:\n{URL_VUELO}"
        )
        enviar_alerta_telegram(mensaje)
        
        # Guarda el nuevo mínimo histórico
        with open(PRECIO_HISTORICO_FILE, "w") as f:
            f.write(str(precio_actual))
            
    elif precio_actual > precio_anterior:
        print("El precio subió. No se envía alerta para evitar spam.")
        # Mantenemos actualizado el archivo con la última tarifa vista
        with open(PRECIO_HISTORICO_FILE, "w") as f:
            f.write(str(precio_actual))
    else:
        print("El precio se mantiene igual desde la última revisión.")


# =====================================================================
# 3. BLOQUE PRINCIPAL
# =====================================================================
if __name__ == "__main__":
    print(f"\n⚡ Iniciando prueba de conexión...")
    enviar_alerta_telegram("¡Hola! Tu bot de vuelos ya está conectado correctamente desde Codespaces. ✈️")    
    
    print(f"\n✈️ Iniciando rastreo de tarifas...")
    precio_detectado = obtener_precio_vuelo()
    
    evaluar_precio(precio_detectado)
    print(f"Monitoreo finalizado correctamente.\n")