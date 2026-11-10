"""
Detecta la ESP32 en macOS.

Uso (desde la carpeta raíz del repo):
    uv run python 00_deteccion_esp/mac.py

En macOS la tarjeta aparece como /dev/cu.usbserial-XXXX, /dev/cu.wchusbserialXXXX,
/dev/cu.SLAB_USBtoUART o /dev/cu.usbmodemXXXX. Usa siempre los que empiezan con
'cu.' (no 'tty.'): los 'tty.' se quedan esperando y parece que nada funciona.
"""

import sys

from comun import ejecutar_diagnostico

CONSEJOS_SIN_PUERTO = [
    "Usa un cable USB de DATOS. Muchos cables solo cargan y la compu no ve nada.",
    "Si usas un adaptador USB-C → USB-A, prueba otro adaptador o un hub distinto.",
    "Revisa si el sistema la ve:  ls /dev/cu.*",
    "En macOS recientes los chips CH340 y CP210x suelen funcionar sin instalar nada.",
    "Si no aparece, mira el chip junto al conector USB de la tarjeta e instala su driver:",
    "   - CP2102 / CP2104  → 'CP210x VCP Mac OSX Driver' de Silicon Labs",
    "   - CH340 / CH9102   → 'CH34xVCPDriver' de WCH",
    "   Después: Ajustes del Sistema → Privacidad y seguridad → 'Permitir' la extensión, y reinicia.",
]

CONSEJOS_SIN_PERMISO = [
    "'Resource busy' = otro programa tiene el puerto abierto.",
    "Cierra Arduino IDE, Thonny, screen, el Monitor Serie de VS Code u otra terminal con mpremote.",
    "Si sigue igual, desconecta la tarjeta, espera 5 segundos y conéctala otra vez.",
]

if __name__ == "__main__":
    sys.exit(ejecutar_diagnostico("Darwin", "macOS", CONSEJOS_SIN_PUERTO, CONSEJOS_SIN_PERMISO))
