# Botviajesnatica
Monitor de precios de vuelos que envía alertas a Telegram cuando el precio baja.

## Configuración segura de credenciales

No pongas `TELEGRAM_TOKEN` ni `TELEGRAM_CHAT_ID` directamente en el código.

Puedes crear un archivo `.env` en la misma carpeta del script con este contenido:

```env
TELEGRAM_TOKEN=tu_token_aqui
TELEGRAM_CHAT_ID=tu_chat_id_aqui
```

El script lee estas variables automáticamente y no las guarda en el repositorio.

## Uso

```bash
python3 monitor_vuelos.py --test
```

```bash
python3 monitor_vuelos.py
```
