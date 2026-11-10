"""
04 · Gráfica en vivo con matplotlib                 (corre EN TU COMPU, Python normal)

Lee las líneas "412,398" que manda 03_esp_a_python/esp_envia.py y las dibuja
como una gráfica que se va moviendo, una línea por sensor:

    lectura
      600 ┤ ───────╮        ╭──────   sensor 1
      400 ┤        │        │
      200 ┤- - - - ╰────────╯- - - -  umbral
        0 ┼──────────────────────────► tiempo
                  ↑ aquí lo tocaste

Correr (con esp_envia.py ya instalado como main.py, ver README):
    uv run python 04_grafica_en_vivo/grafica.py           ← busca la ESP32 sola
    uv run python 04_grafica_en_vivo/grafica.py COM5      ← o dile el puerto

Detener: cierra la ventana de la gráfica.
"""

import sys
from collections import deque

if sys.implementation.name == "micropython":   # lo mandaron a la ESP32 por error
    raise SystemExit("Este script corre EN TU COMPU. Usa:\n"
                     "  uv run python 04_grafica_en_vivo/grafica.py")

try:
    import matplotlib.pyplot as plt
    import serial
    from matplotlib.animation import FuncAnimation
    from serial.tools import list_ports
except ImportError:                            # se corrió sin uv run, o falta uv sync
    raise SystemExit("Faltan librerías. Desde la raíz del repo corre:\n"
                     "  uv sync\n"
                     "  uv run python 04_grafica_en_vivo/grafica.py")

VELOCIDAD = 115200
PUNTOS = 200            # cuántas lecturas se ven a la vez (200 × 50 ms = 10 s)
UMBRAL_TOQUE = 200      # menor a esto = tocado (ESP32 clásica); ajústalo a tus cables
CADA_MS = 50            # cada cuánto se redibuja la gráfica

# Chips USB de las ESP32 más comunes (los mismos que en 00_deteccion_esp)
VIDS_ESP32 = {0x10C4, 0x1A86, 0x0403, 0x303A}


# ---------------------------------------------------------------------------
# 1. Conexión con la ESP32 (igual que en la 03)
# ---------------------------------------------------------------------------
def buscar_puerto():
    """Regresa el primer puerto que parezca una ESP32, o None."""
    for puerto in list_ports.comports():
        if puerto.vid in VIDS_ESP32:
            return puerto.device
    return None


def abrir_puerto(puerto):
    """Abre el puerto sin reiniciar la ESP32 y sin bloquear al leer."""
    conexion = serial.Serial()
    conexion.port = puerto
    conexion.baudrate = VELOCIDAD
    conexion.timeout = 0          # read() regresa al instante con lo que haya
    conexion.dtr = False
    conexion.rts = False
    conexion.open()
    return conexion


def interpretar(linea):
    """'412,398' → [412, 398].  Si la línea no son números, regresa None."""
    try:
        return [int(parte) for parte in linea.split(",")]
    except ValueError:
        return None


def leer_nuevos(conexion, pendiente):
    """
    Lee todo lo que llegó desde la última vez.
    'pendiente' es el pedazo de línea que quedó incompleto la vez anterior.
    Regresa (lista de lecturas completas, nuevo pedazo pendiente).
    """
    pendiente += conexion.read(conexion.in_waiting or 1)
    *lineas_completas, pendiente = pendiente.split(b"\n")

    lecturas = []
    for linea in lineas_completas:
        valores = interpretar(linea.decode(errors="ignore").strip())
        if valores:
            lecturas.append(valores)
    return lecturas, pendiente


# ---------------------------------------------------------------------------
# 2. La gráfica
# ---------------------------------------------------------------------------
def crear_grafica(conexion):
    """Prepara la figura y regresa (figura, función que la actualiza)."""
    figura, ejes = plt.subplots(figsize=(9, 4.5))
    ejes.set_xlabel(f"lecturas (una cada ~50 ms, se ven las últimas {PUNTOS})")
    ejes.set_ylabel("valor del sensor touch")
    ejes.set_xlim(0, PUNTOS)
    ejes.set_ylim(0, 1000)
    ejes.axhline(UMBRAL_TOQUE, linestyle="--", color="gray", label="umbral de toque")
    ejes.grid(alpha=0.3)
    ejes.set_title("Esperando datos de la ESP32...")

    historias = []      # una deque por sensor: guarda solo las últimas PUNTOS lecturas
    lineas = []         # una línea de matplotlib por sensor
    pendiente = b""

    def agregar_sensores(cuantos):
        """La primera vez que llegan datos, crea una línea por sensor."""
        for numero in range(1, cuantos + 1):
            historias.append(deque(maxlen=PUNTOS))
            (linea,) = ejes.plot([], [], linewidth=2, label=f"sensor {numero}")
            lineas.append(linea)
        ejes.legend(loc="upper right")

    def actualizar(_cuadro):
        nonlocal pendiente
        lecturas, pendiente = leer_nuevos(conexion, pendiente)

        for valores in lecturas:
            if not historias:
                agregar_sensores(len(valores))
            for historia, valor in zip(historias, valores):
                historia.append(valor)

        if not historias or not historias[0]:
            return lineas

        for linea, historia in zip(lineas, historias):
            linea.set_data(range(len(historia)), historia)

        # Ajusta el eje Y a lo que se está viendo
        mas_alto = max(max(historia) for historia in historias)
        ejes.set_ylim(0, max(mas_alto * 1.4, UMBRAL_TOQUE * 2))   # espacio para la leyenda

        # Título: quién está siendo tocado ahora
        tocados = [str(i) for i, h in enumerate(historias, start=1) if h[-1] < UMBRAL_TOQUE]
        if tocados:
            ejes.set_title("TOCANDO sensor " + ", ".join(tocados), color="crimson")
        else:
            ejes.set_title("Sin tocar", color="black")
        return lineas

    return figura, actualizar


# ---------------------------------------------------------------------------
# 3. Programa principal
# ---------------------------------------------------------------------------
def main():
    puerto = sys.argv[1] if len(sys.argv) > 1 else buscar_puerto()
    if puerto is None:
        print("No encontré la ESP32. Corre primero el script de 00_deteccion_esp/.")
        return 1

    print(f"Escuchando {puerto}. Cierra la ventana de la gráfica para salir.")
    with abrir_puerto(puerto) as conexion:
        figura, actualizar = crear_grafica(conexion)
        # Guardamos la animación en una variable: si no, Python la borra y no se mueve
        animacion = FuncAnimation(figura, actualizar, interval=CADA_MS, cache_frame_data=False)
        plt.show()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except serial.SerialException as error:
        print(f"Problema con el puerto: {error}")
        print("¿Hay otra terminal con mpremote o pc_grafica.py abierta? Ciérrala.")
        sys.exit(1)
