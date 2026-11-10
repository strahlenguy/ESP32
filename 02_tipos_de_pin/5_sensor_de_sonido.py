"""
02.5 · SENSOR (ADC) — medir ruido con un micrófono  (corre EN la ESP32, MicroPython)

Módulo de micrófono tipo KY-038 / KY-037 (el de la perilla azul).
Su salida analógica (AO) se queda en un voltaje "de reposo" y oscila alrededor
cuando hay sonido. Más ruido = oscilación más grande. Así que medimos la
diferencia entre la lectura más alta y la más baja en un instante: la AMPLITUD.

Circuito:
    módulo  +  ── 3V3          (NO a 5 V: su salida le llegaría a la ESP32 a 5 V)
    módulo  G  ── GND
    módulo  AO ── GPIO35
    módulo  DO ── (no se usa aquí; es un sí/no ajustable con la perilla)

Correr:
    uv run mpremote run 02_tipos_de_pin/5_sensor_de_sonido.py
"""

import time

try:
    from machine import ADC, Pin
except ImportError:  # estás en tu compu, no en la ESP32
    raise SystemExit("Este script corre EN la ESP32. Usa:\n"
                     "  uv run mpremote run 02_tipos_de_pin/5_sensor_de_sonido.py")

mic = ADC(Pin(35))
mic.atten(ADC.ATTN_11DB)

MUESTRAS = 200        # lecturas por "instante" (~unos milisegundos)


def medir_amplitud():
    """Lee MUESTRAS veces y regresa (máximo - mínimo)."""
    minimo = 65535
    maximo = 0
    for _ in range(MUESTRAS):
        lectura = mic.read_u16()
        if lectura < minimo:
            minimo = lectura
        if lectura > maximo:
            maximo = lectura
    return maximo - minimo


print("Aplaude, chifla o habla cerca del micrófono (Ctrl+C para salir)")

while True:
    amplitud = medir_amplitud()
    barra = "#" * min(amplitud // 500, 40)
    print(f"{amplitud:6d} {barra}")
    time.sleep_ms(50)
