"""
Detecta la ESP32 en Linux.

Uso (desde la carpeta raíz del repo):
    uv run python 00_deteccion_esp/linux.py

En Linux la tarjeta aparece como /dev/ttyUSB0 (CP210x, CH340) o /dev/ttyACM0 (USB nativo).
Lo que más falla en Linux son los PERMISOS, así que este script los revisa antes.
"""

import grp
import os
import shutil
import sys

from comun import ejecutar_diagnostico

# Ubuntu/Debian/Mint usan 'dialout'; Arch/Manjaro usan 'uucp'
GRUPOS_SERIE = ("dialout", "uucp")


def revisar_permisos_y_conflictos():
    """Revisiones que solo tienen sentido en Linux."""
    mis_grupos = set()
    for gid in os.getgroups():
        try:
            mis_grupos.add(grp.getgrgid(gid).gr_name)
        except KeyError:
            pass  # grupo sin nombre; lo ignoramos
    grupos_existentes = [g for g in GRUPOS_SERIE if _grupo_existe(g)]

    if any(g in mis_grupos for g in grupos_existentes):
        print("✅ Tu usuario está en el grupo de puertos serie.\n")
    elif grupos_existentes:
        grupo = grupos_existentes[0]
        print(f"⚠️  Tu usuario NO está en el grupo '{grupo}'. Probablemente no podrás abrir el puerto.")
        print(f"   Arréglalo con:  sudo usermod -aG {grupo} $USER")
        print("   y luego CIERRA SESIÓN y vuelve a entrar (o reinicia).\n")

    if shutil.which("brltty"):
        print("⚠️  Tienes 'brltty' instalado (lector braille). En Ubuntu suele 'robarse'")
        print("   las tarjetas con chip CH340 y el puerto desaparece al instante.")
        print("   Si no usas un lector braille:  sudo apt remove brltty\n")


def _grupo_existe(nombre):
    try:
        grp.getgrnam(nombre)
        return True
    except KeyError:
        return False


CONSEJOS_SIN_PUERTO = [
    "Usa un cable USB de DATOS. Muchos cables solo cargan y la compu no ve nada.",
    "Conecta la tarjeta y corre:  sudo dmesg | tail -20",
    "   - si ves 'ch341-uart converter now attached' y luego 'disconnected', es brltty (ver arriba)",
    "   - si no aparece nada, es el cable o el puerto USB",
    "Revisa si existe el dispositivo:  ls /dev/ttyUSB* /dev/ttyACM*",
]

CONSEJOS_SIN_PERMISO = [
    "'Permission denied' = tu usuario no está en el grupo dialout (o uucp en Arch).",
    "   sudo usermod -aG dialout $USER   y después cierra sesión y vuelve a entrar.",
    "'Device or resource busy' = otro programa usa el puerto "
    "(Arduino IDE, Thonny, screen, otra terminal con mpremote). Ciérralo.",
]

if __name__ == "__main__":
    sys.exit(ejecutar_diagnostico("Linux", "Linux", CONSEJOS_SIN_PUERTO, CONSEJOS_SIN_PERMISO,
                                  revision_extra=revisar_permisos_y_conflictos))
