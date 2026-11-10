"""
Funciones compartidas por windows.py, linux.py y mac.py.

No lo corras directamente: corre el script de TU sistema operativo.
Cada script solo cambia los consejos que te da si algo falla;
la detección en sí es igual en los tres sistemas.
"""

import platform
import sys
import time

import serial
from serial.tools import list_ports

# Chips USB-serie que traen las tarjetas ESP32 más comunes.
# Cada puerto USB dice quién lo fabricó (VID) y qué producto es (PID).
CHIPS_CONOCIDOS = {
    (0x10C4, 0xEA60): "Silicon Labs CP210x",
    (0x1A86, 0x7523): "WCH CH340",
    (0x1A86, 0x55D4): "WCH CH9102",
    (0x0403, 0x6001): "FTDI FT232",
}
VID_ESPRESSIF = 0x303A  # ESP32-S2 / S3 / C3 con USB nativo (sin chip intermedio)


# ---------------------------------------------------------------------------
# 1. Buscar la tarjeta
# ---------------------------------------------------------------------------
def nombre_del_chip(puerto):
    """Regresa el nombre del chip USB si parece una ESP32, o None."""
    if puerto.vid is None:
        return None
    if puerto.vid == VID_ESPRESSIF:
        return "USB nativo de Espressif"
    return CHIPS_CONOCIDOS.get((puerto.vid, puerto.pid))


def buscar_esp32():
    """Lista de (puerto, chip) que parecen ser una ESP32."""
    encontrados = []
    for puerto in list_ports.comports():
        chip = nombre_del_chip(puerto)
        if chip is not None:
            encontrados.append((puerto, chip))
    return encontrados


def mostrar_todos_los_puertos():
    """Imprime todos los puertos serie, aunque no parezcan ESP32."""
    puertos = list_ports.comports()
    if not puertos:
        print("   (no hay ningún puerto serie en el sistema)")
        return
    for p in puertos:
        ids = f"{p.vid:04X}:{p.pid:04X}" if p.vid is not None else "sin VID/PID"
        print(f"   - {p.device:<28} {ids:<12} {p.description}")


# ---------------------------------------------------------------------------
# 2. Hablar con la tarjeta
# ---------------------------------------------------------------------------
def abrir_puerto(dispositivo):
    """Abre el puerto sin reiniciar la ESP32 (DTR y RTS apagados)."""
    conexion = serial.Serial()
    conexion.port = dispositivo
    conexion.baudrate = 115200
    conexion.timeout = 0.3
    conexion.dtr = False
    conexion.rts = False
    conexion.open()
    return conexion


def preguntar_a_micropython(conexion, intentos=3):
    """
    Le pide a la ESP32 que diga qué es. Si tiene MicroPython responde algo como
    'ESP: Generic ESP32 module with ESP32 | 1.29.0'. Si no, regresa None.
    """
    # 'ES' + 'P:' para no confundir el eco del comando con la respuesta
    comando = b"import os; print('ES' + 'P:', os.uname().machine, '|', os.uname().release)\r\n"
    for _ in range(intentos):
        conexion.write(b"\r\x03\x03")  # Ctrl+C dos veces: detiene lo que esté corriendo
        time.sleep(0.3)
        conexion.reset_input_buffer()
        conexion.write(comando)

        limite = time.time() + 1.0
        recibido = b""
        while time.time() < limite:
            recibido += conexion.read(256)
            lineas_completas = recibido.decode(errors="ignore").split("\n")[:-1]
            for linea in lineas_completas:
                if linea.startswith("ESP:"):
                    return linea[4:].strip()
        time.sleep(0.5)  # quizá se estaba reiniciando; damos otra oportunidad
    return None


# ---------------------------------------------------------------------------
# 3. El diagnóstico completo (lo llaman windows.py, linux.py y mac.py)
# ---------------------------------------------------------------------------
def imprimir_consejos(titulo, consejos):
    print(f"\n{titulo}")
    for consejo in consejos:
        if consejo.startswith(" "):      # renglón de detalle: sin viñeta
            print(f"   {consejo}")
        else:
            print(f"   • {consejo}")


def ejecutar_diagnostico(sistema_esperado, nombre_sistema, consejos_sin_puerto,
                         consejos_sin_permiso, revision_extra=None):
    """
    sistema_esperado: lo que regresa platform.system() ('Windows', 'Linux', 'Darwin')
    revision_extra:   función opcional con revisiones propias del sistema
    Regresa 0 si todo salió bien, 1 si hubo un problema (código de salida).
    """
    print(f"== Detección de ESP32 en {nombre_sistema} ==\n")

    if platform.system() != sistema_esperado:
        print(f"⚠️  Este script es para {nombre_sistema}, pero estás en {platform.system()}.")
        print("   Corre el script de tu sistema: windows.py, linux.py o mac.py\n")

    print(f"Python {platform.python_version()} · pyserial {serial.VERSION}\n")

    if revision_extra is not None:
        revision_extra()

    # Paso 1: ¿el sistema ve la tarjeta?
    print("[1/2] Buscando la ESP32 en los puertos USB...")
    encontrados = buscar_esp32()
    if not encontrados:
        print("❌ No encontré ninguna ESP32.\n\n   Puertos que sí ve tu sistema:")
        mostrar_todos_los_puertos()
        imprimir_consejos("Qué revisar:", consejos_sin_puerto)
        return 1

    for puerto, chip in encontrados:
        print(f"✅ Encontrada en {puerto.device}  (chip USB: {chip})")
    if len(encontrados) > 1:
        print("   Hay más de una; voy a probar con la primera.")
    puerto, _ = encontrados[0]

    # Paso 2: ¿podemos hablar con ella?
    print(f"\n[2/2] Hablando con la ESP32 en {puerto.device}...")
    try:
        conexion = abrir_puerto(puerto.device)
    except serial.SerialException as error:
        print(f"❌ No pude abrir el puerto: {error}")
        imprimir_consejos("Qué revisar:", consejos_sin_permiso)
        return 1

    with conexion:
        respuesta = preguntar_a_micropython(conexion)

    if respuesta is None:
        print("🟡 El puerto abre bien, pero la ESP32 no respondió como MicroPython.")
        print("   Es normal si todavía no le instalas MicroPython:")
        print("   sigue el paso 'Instalar MicroPython' de INSTALACION.md y vuelve a correr esto.")
        return 1

    maquina, _, version = respuesta.partition("|")
    print(f"✅ Respondió MicroPython {version.strip()}")
    print(f"   Tarjeta: {maquina.strip()}")
    print(f"\n🎉 Todo listo. Usa este puerto si alguna herramienta te lo pide: {puerto.device}")
    return 0


if __name__ == "__main__":
    print("Corre el script de tu sistema: windows.py, linux.py o mac.py")
    sys.exit(1)
