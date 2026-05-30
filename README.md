# Botviajesnatica
Monitor de precios de vuelos que envía alertas a Telegram cuando el precio baja.

## 🚀 Automatización con GitHub Actions

El repositorio ahora incluye un workflow automatizado que ejecuta el monitor **cada día a las 9 AM UTC** (6 AM de Santiago).

### Pasos para configurar:

1. **Sube el repositorio a GitHub** (si aún no lo has hecho):
   ```bash
   git remote add origin https://github.com/TU_USUARIO/Botviajesnatica.git
   git branch -M main
   git push -u origin main
   ```

2. **Configura los secrets en GitHub:**
   - Ve a `Settings` → `Secrets and variables` → `Actions`
   - Crea dos secretos nuevos:
     - `TELEGRAM_TOKEN`: Tu token de bot de Telegram
     - `TELEGRAM_CHAT_ID`: El ID de tu chat

3. **Listo.** El script se ejecutará automáticamente cada día.

### Monitoreo del workflow:
- Ve a `Actions` en tu repositorio para ver el historial de ejecuciones
- Los cambios de precio se commitearán automáticamente en el archivo `ultimo_precio.txt`

---

## ⚙️ Configuración local

### Requisitos
- Python 3.9+
- `fast-flights` y `requests`

```bash
pip install fast-flights requests
```

### Configuración segura de credenciales

No pongas `TELEGRAM_TOKEN` ni `TELEGRAM_CHAT_ID` directamente en el código.

Crea un archivo `.env` en la misma carpeta del script:

```env
TELEGRAM_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

El script lee estas variables automáticamente y `.env` no se guarda en el repositorio.

## 📋 Uso

### Ejecución manual:

**Enviar alerta de prueba:**
```bash
python3 monitor_vuelos.py --test
```

**Verificar precio actual:**
```bash
python3 monitor_vuelos.py
```

## 🎯 Características

- ✈️ Monitorea vuelos round-trip usando `fast-flights`
- 💰 Compara precios y envía alerta solo si hay una **bajada significativa** (umbral: $1.000)
- 🔄 Automatización diaria sin intervención manual
- 💾 Persistencia de datos en `ultimo_precio.txt`
- 🛡️ Manejo robusto de errores (archivos corrupto, conexión fallida, etc.)

## 📝 Personalización

Puedes ajustar estos parámetros en `monitor_vuelos.py`:

```python
ORIGEN  = "SCL"           # Aeropuerto de origen
DESTINO = "GIG"           # Aeropuerto de destino
SALIDA  = "2026-06-24"    # Fecha de salida (YYYY-MM-DD)
REGRESO = "2026-06-29"    # Fecha de regreso (YYYY-MM-DD)
UMBRAL_BAJADA = 1000      # Mínimo de bajada para alerta (pesos)
```

## 🐛 Resolución de problemas

Si el workflow falla:
1. Verifica que `TELEGRAM_TOKEN` y `TELEGRAM_CHAT_ID` estén configurados correctamente
2. Revisa los logs en la pestaña `Actions` del repositorio
3. Prueba manualmente: `python3 monitor_vuelos.py --test`

