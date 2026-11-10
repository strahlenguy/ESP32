"""
Detecta la ESP32 en Windows.

Uso (desde la carpeta raíz del repo):
    uv run python 00_deteccion_esp/windows.py

En Windows la tarjeta aparece como un puerto COM (COM3, COM4, ...).
"""

import sys

from comun import ejecutar_diagnostico

CONSEJOS_SIN_PUERTO = [
    "Usa un cable USB de DATOS. Muchos cables solo cargan y la compu no ve nada.",
    "Abre el Administrador de dispositivos → 'Puertos (COM y LPT)'. "
    "Si la ves en 'Otros dispositivos' con un ⚠️, te falta el driver.",
    "Mira el chip pequeño junto al conector USB de la tarjeta:",
    "   - dice CP2102 / CP2104  → driver 'CP210x Universal Windows Driver' de Silicon Labs",
    "   - dice CH340 / CH9102   → driver 'CH341SER' de WCH (wch-ic.com)",
    "Después de instalar el driver, desconecta y vuelve a conectar la tarjeta.",
    "Prueba otro puerto USB (de preferencia directo a la compu, sin hub).",
]

CONSEJOS_SIN_PERMISO = [
    "'Acceso denegado' casi siempre significa que OTRO programa tiene el puerto abierto.",
    "Cierra Arduino IDE, Thonny, PuTTY, el Monitor Serie de VS Code u otra terminal con mpremote.",
    "Si sigue igual, desconecta la tarjeta, espera 5 segundos y conéctala otra vez.",
]

if __name__ == "__main__":
    sys.exit(ejecutar_diagnostico("Windows", "Windows", CONSEJOS_SIN_PUERTO, CONSEJOS_SIN_PERMISO))
