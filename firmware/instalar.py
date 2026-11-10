"""
Instala MicroPython en la ESP32 con un solo comando.

Uso (desde la carpeta raíz del repo, con la ESP32 conectada):
    uv run python firmware/instalar.py

Qué hace:
    1. Busca el firmware (.bin) en esta carpeta. Si no hay, descarga el último
       estable de micropython.org y lo guarda aquí.
    2. Encuentra tu ESP32.
    3. Borra su memoria y le graba MicroPython (con esptool).
    4. Comprueba que MicroPython responda.

Solo hace falta una vez por tarjeta. Funciona con la ESP32 clásica (ESP32-WROOM-32).
"""

import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

CARPETA_FIRMWARE = Path(__file__).resolve().parent
PAGINA_DESCARGAS = "https://micropython.org/download/ESP32_GENERIC/"
DIRECCION_FLASH = "0x1000"   # ESP32 clásica. (ESP32-S3 / C3 usarían 0x0)

# Reutilizamos la detección de 00_deteccion_esp/comun.py
sys.path.insert(0, str(CARPETA_FIRMWARE.parent / "00_deteccion_esp"))
from comun import abrir_puerto, buscar_esp32, preguntar_a_micropython  # noqa: E402


def firmware_local():
    """El .bin más nuevo que haya en firmware/, o None."""
    archivos = sorted(CARPETA_FIRMWARE.glob("ESP32_GENERIC-*.bin"))
    return archivos[-1] if archivos else None


def descargar_firmware():
    """Descarga el último firmware estable de MicroPython para ESP32."""
    print(f"Buscando la versión más reciente en {PAGINA_DESCARGAS} ...")
    pedido = urllib.request.Request(PAGINA_DESCARGAS, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(pedido, timeout=30) as respuesta:
        html = respuesta.read().decode("utf-8", errors="ignore")

    # Estables: ESP32_GENERIC-20250415-v1.25.0.bin  (las "preview" llevan otro sufijo)
    enlaces = re.findall(r'/resources/firmware/(ESP32_GENERIC-\d{8}-v[\d.]+\.bin)"', html)
    if not enlaces:
        raise RuntimeError("No encontré el firmware en la página de MicroPython.")
    nombre = max(enlaces)   # la fecha va en el nombre: el mayor es el más nuevo

    destino = CARPETA_FIRMWARE / nombre
    print(f"Descargando {nombre} ...")
    pedido = urllib.request.Request(
        f"https://micropython.org/resources/firmware/{nombre}",
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(pedido, timeout=120) as respuesta:
        destino.write_bytes(respuesta.read())
    print(f"✅ Guardado en firmware/{nombre}\n")
    return destino


def esptool(*argumentos):
    """Corre esptool con el mismo Python del proyecto. Regresa True si salió bien."""
    comando = [sys.executable, "-m", "esptool", *argumentos]
    return subprocess.run(comando).returncode == 0


def main():
    print("== Instalar MicroPython en la ESP32 ==\n")

    # 1. Firmware
    bin_firmware = firmware_local()
    if bin_firmware:
        print(f"Firmware: firmware/{bin_firmware.name}\n")
    else:
        try:
            bin_firmware = descargar_firmware()
        except Exception as error:
            print(f"❌ No pude descargar el firmware: {error}")
            print(f"   Descárgalo a mano de {PAGINA_DESCARGAS}")
            print("   y guárdalo en la carpeta firmware/ del repo.")
            return 1

    # 2. Tarjeta
    encontrados = buscar_esp32()
    if not encontrados:
        print("❌ No encontré ninguna ESP32. Corre primero:")
        print("   uv run python 00_deteccion_esp/windows.py")
        return 1
    puerto = encontrados[0][0].device
    print(f"ESP32 encontrada en {puerto}\n")

    respuesta = input("Se va a BORRAR todo lo que tenga la ESP32. ¿Continuar? [s/N] ")
    if respuesta.strip().lower() not in ("s", "si", "sí"):
        print("Cancelado.")
        return 1

    # 3. Borrar y grabar
    print("\n[1/2] Borrando la memoria...")
    if not esptool("--port", puerto, "erase-flash"):
        print("\n❌ Falló el borrado.")
        print("   Intenta de nuevo manteniendo presionado el botón BOOT")
        print("   mientras aparece 'Connecting....'.")
        return 1

    print("\n[2/2] Grabando MicroPython...")
    grabado = esptool("--port", puerto, "--baud", "460800",
                      "write-flash", DIRECCION_FLASH, str(bin_firmware))
    if not grabado:
        print("\nFalló a velocidad alta; reintentando más lento...")
        grabado = esptool("--port", puerto, "write-flash", DIRECCION_FLASH, str(bin_firmware))
    if not grabado:
        print("\n❌ No se pudo grabar. Revisa el cable y prueba con el botón BOOT.")
        return 1

    # 4. Comprobar
    print("\nComprobando...")
    time.sleep(2)   # la ESP32 se reinicia después de grabar
    with abrir_puerto(puerto) as conexion:
        version = preguntar_a_micropython(conexion)
    if version is None:
        print("🟡 Se grabó, pero MicroPython no respondió todavía.")
        print("   Presiona el botón EN de la tarjeta y corre la detección otra vez.")
        return 1

    print(f"🎉 Listo: MicroPython {version.partition('|')[2].strip()} instalado.")
    print("   Siguiente paso: uv run mpremote run 01_led_parpadeo/parpadeo.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
