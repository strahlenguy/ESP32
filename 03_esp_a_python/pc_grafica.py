"""
03 · Tu compu RECIBE los datos de la ESP32          (corre EN TU COMPU, Python normal)

Lee las líneas "412,398" que manda esp_envia.py y dibuja una barra por sensor:

    sensor 1  ███████████████████████████        412
    sensor 2  ████████                           120  👆

Correr (primero instala esp_envia.py como main.py, ver su encabezado):
    uv run python 03_esp_a_python/pc_grafica.py            ← busca la ESP32 sola
    uv run python 03_esp_a_python/pc_grafica.py COM5       ← o dile el puerto

Detener: Ctrl+C.

Para el proyecto final, cambia la función dibujar() por tu propio visualizador
(matplotlib, pygame, tkinter, sonido...). Lo demás casi no cambia.
"""

import sys

if sys.implementation.name == "micropython":   # lo mandaron a la ESP32 por error
    raise SystemExit("Este script corre EN TU COMPU. Usa:\n"
                     "  uv run python 03_esp_a_python/pc_grafica.py")

try:
    import serial
    from serial.tools import list_ports
except ImportError:                            # se corrió sin uv run
    raise SystemExit("Falta pyserial. Corre el script con uv desde la raíz del repo:\n"
                     "  uv sync\n"
                     "  uv run python 03_esp_a_python/pc_grafica.py")

VELOCIDAD = 115200
ANCHO_BARRA = 40
VALOR_MAXIMO = 800      # ajústalo según los números que veas
UMBRAL_TOQUE = 200      # menor a esto = tocado (ESP32 clásica)

# Chips USB de las ESP32 más comunes (los mismos que en 00_deteccion_esp)
VIDS_ESP32 = {0x10C4, 0x1A86, 0x0403, 0x303A}


def buscar_puerto():
    """Regresa el primer puerto que parezca una ESP32, o None."""
    for puerto in list_ports.comports():
        if puerto.vid in VIDS_ESP32:
            return puerto.device
    return None


def interpretar(linea):
    """'412,398' → [412, 398].  Si la línea no son números, regresa None."""
    try:
        return [int(parte) for parte in linea.split(",")]
    except ValueError:
        return None  # mensajes de arranque de la ESP32, basura, etc.


def dibujar(valores):
    """Imprime una barra por sensor. Reemplaza esto por tu visualizador."""
    for i, valor in enumerate(valores, start=1):
        largo = min(valor * ANCHO_BARRA // VALOR_MAXIMO, ANCHO_BARRA)
        barra = "█" * largo
        marca = "👆" if valor < UMBRAL_TOQUE else ""
        print(f"sensor {i}  {barra:<{ANCHO_BARRA}} {valor:5d}  {marca}")
    print()


def main():
    puerto = sys.argv[1] if len(sys.argv) > 1 else buscar_puerto()
    if puerto is None:
        print("No encontré la ESP32. Corre primero el script de 00_deteccion_esp/.")
        return 1

    print(f"Escuchando {puerto} a {VELOCIDAD} baudios (Ctrl+C para salir)\n")
    conexion = serial.Serial()
    conexion.port = puerto
    conexion.baudrate = VELOCIDAD
    conexion.timeout = 1
    conexion.dtr = False      # DTR/RTS apagados: así no reiniciamos la ESP32 al abrir
    conexion.rts = False
    conexion.open()

    with conexion:
        while True:
            linea = conexion.readline().decode(errors="ignore").strip()
            valores = interpretar(linea)
            if valores:
                dibujar(valores)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nAdiós 👋")
    except serial.SerialException as error:
        print(f"Problema con el puerto: {error}")
        print("¿Hay otra terminal con mpremote abierta? Ciérrala y vuelve a intentar.")
        sys.exit(1)
