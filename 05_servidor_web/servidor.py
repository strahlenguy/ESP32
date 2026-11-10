"""
05 · Servidor web en la ESP32                       (corre EN la ESP32, MicroPython)

La ESP32 crea su propia red WiFi y sirve una página web. Desde el celular o la
laptop ves los sensores touch en vivo y prendes/apagas el LED, sin cables.

    📱 navegador ──WiFi──► ESP32 ──► página web, /datos, /led/on, /led/off

Circuito: el de la 01 + los cables touch de la 03
    GPIO23 ──[ 220 Ω ]──►|── GND        LED
    GPIO4  ── cable 1                  touch
    GPIO27 ── cable 2                  touch

Correr:
    uv run mpremote run 05_servidor_web/servidor.py
Luego:
    1. En tu celular/laptop conéctate a la red WiFi NOMBRE_RED (clave: CLAVE)
    2. Abre en el navegador la dirección que imprime la terminal (http://192.168.4.1)

Detener: Ctrl+C en la terminal y luego el botón EN de la tarjeta.
"""

import json
import socket
import time

try:
    import network
    from machine import Pin, TouchPad
except ImportError:  # estás en tu compu, no en la ESP32
    raise SystemExit("Este script corre EN la ESP32. Usa:\n"
                     "  uv run mpremote run 05_servidor_web/servidor.py")

# ---------------------------------------------------------------------------
# Configuración  ← cambia esto
# ---------------------------------------------------------------------------
MODO = "ap"                  # "ap":   la ESP32 crea su propia red (funciona en cualquier lado)
                             # "wifi": la ESP32 se conecta a una red que ya existe
NOMBRE_RED = "ESP32-equipo1" # ⚠️ cada equipo un nombre distinto
CLAVE = "proyecto123"        # mínimo 8 caracteres

WIFI_RED = "NombreDeTuWiFi"  # solo si MODO = "wifi"
WIFI_CLAVE = "ClaveDeTuWiFi"

UMBRAL_TOQUE = 200           # menor a esto = tocado (igual que en la 03 y la 04)

# ---------------------------------------------------------------------------
# Hardware
# ---------------------------------------------------------------------------
led = Pin(23, Pin.OUT)
sensores = [TouchPad(Pin(4)), TouchPad(Pin(27))]


# ---------------------------------------------------------------------------
# 1. Red WiFi
# ---------------------------------------------------------------------------
def direccion_ip(interfaz):
    try:
        return interfaz.ipconfig("addr4")[0]   # MicroPython 1.24 o más nuevo
    except (AttributeError, ValueError):
        return interfaz.ifconfig()[0]          # versiones anteriores


def crear_red_propia():
    """Modo punto de acceso: la ESP32 es el 'módem'."""
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid=NOMBRE_RED, password=CLAVE, authmode=network.AUTH_WPA2_PSK)
    while not ap.active():
        time.sleep(0.1)
    print("📶 Red WiFi creada:", NOMBRE_RED, " clave:", CLAVE)
    return direccion_ip(ap)


def conectar_a_wifi():
    """Modo estación: la ESP32 se une a una red existente (casa, celular)."""
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(WIFI_RED, WIFI_CLAVE)
    print("Conectando a", WIFI_RED, end="")
    for _ in range(40):               # hasta 20 segundos
        if sta.isconnected():
            print(" ✅")
            return direccion_ip(sta)
        print(".", end="")
        time.sleep(0.5)
    raise SystemExit("\n❌ No se pudo conectar. Revisa WIFI_RED y WIFI_CLAVE "
                     "(las redes de la escuela con usuario y contraseña no funcionan).")


# ---------------------------------------------------------------------------
# 2. La página web (HTML + un poquito de JavaScript)
# ---------------------------------------------------------------------------
PAGINA = """<!DOCTYPE html>
<html lang="es"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>ESP32</title>
<style>
 body{font-family:system-ui,sans-serif;max-width:420px;margin:24px auto;padding:0 16px;background:#f4f4f2;color:#222}
 h1{font-size:1.4em} .tarjeta{background:#fff;border-radius:12px;padding:14px 16px;margin:12px 0;box-shadow:0 1px 3px #0002}
 .barra{height:14px;background:#e5e5e5;border-radius:7px;overflow:hidden;margin-top:8px}
 .relleno{height:100%;width:0;background:#3b82f6;transition:width .2s}
 .tocado .relleno{background:#e11d48} .tocado b{color:#e11d48}
 button{font-size:1.1em;padding:12px 0;width:48%;border:0;border-radius:10px;color:#fff;cursor:pointer}
 #on{background:#16a34a} #off{background:#555}
</style></head><body>
<h1>Mi ESP32 🍌</h1>
<div id="sensores"></div>
<div class="tarjeta">LED: <b id="estado-led">?</b><br><br>
 <button id="on" onclick="fetch('/led/on')">Prender</button>
 <button id="off" onclick="fetch('/led/off')">Apagar</button>
</div>
<script>
async function actualizar(){
  try{
    const d = await (await fetch('/datos')).json();
    let html = '';
    d.sensores.forEach((v, i) => {
      const tocado = v < d.umbral;
      const ancho = Math.min(100, v / 8);
      html += `<div class="tarjeta ${tocado ? 'tocado' : ''}">Sensor ${i+1}: <b>${v}</b> ${tocado ? '👆 TOCADO' : ''}
               <div class="barra"><div class="relleno" style="width:${ancho}%"></div></div></div>`;
    });
    document.getElementById('sensores').innerHTML = html;
    document.getElementById('estado-led').textContent = d.led ? 'prendido' : 'apagado';
  }catch(e){}
  setTimeout(actualizar, 300);
}
actualizar();
</script></body></html>"""


# ---------------------------------------------------------------------------
# 3. El servidor
# ---------------------------------------------------------------------------
def leer_datos():
    """Lo que la página pide cada 300 ms, como texto JSON."""
    return json.dumps({
        "sensores": [sensor.read() for sensor in sensores],
        "led": led.value(),
        "umbral": UMBRAL_TOQUE,
    })


def responder(cliente, cuerpo, tipo="text/html", estado="200 OK"):
    encabezado = f"HTTP/1.0 {estado}\r\nContent-Type: {tipo}; charset=utf-8\r\n\r\n"
    cliente.sendall(encabezado.encode())
    cliente.sendall(cuerpo.encode())


def atender(cliente):
    """Lee qué pidió el navegador y contesta según la ruta."""
    pedido = cliente.recv(1024).decode()       # ej. "GET /led/on HTTP/1.1 ..."
    partes = pedido.split(" ")
    ruta = partes[1] if len(partes) > 1 else "/"

    if ruta == "/":
        responder(cliente, PAGINA)
    elif ruta == "/datos":
        responder(cliente, leer_datos(), "application/json")
    elif ruta == "/led/on":
        led.on()
        responder(cliente, "ok", "text/plain")
    elif ruta == "/led/off":
        led.off()
        responder(cliente, "ok", "text/plain")
    else:
        responder(cliente, "No existe", "text/plain", "404 Not Found")
    return ruta


def iniciar_servidor(ip, puerto=80):
    servidor = socket.socket()
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.bind(socket.getaddrinfo("0.0.0.0", puerto)[0][-1])
    servidor.listen(5)
    print(f"🌐 Abre en el navegador:  http://{ip}" + ("" if puerto == 80 else f":{puerto}"))

    while True:
        cliente, direccion = servidor.accept()   # espera a que alguien se conecte
        cliente.settimeout(2)                    # si no manda nada en 2 s, lo soltamos
        try:
            ruta = atender(cliente)
            if ruta != "/datos":                 # /datos llega cada 300 ms: no lo imprimimos
                print(direccion[0], "pidió", ruta)
        except OSError:
            pass                                 # el navegador cerró antes de tiempo
        finally:
            cliente.close()


# ---------------------------------------------------------------------------
# Programa principal
# ---------------------------------------------------------------------------
ip = crear_red_propia() if MODO == "ap" else conectar_a_wifi()
iniciar_servidor(ip)
