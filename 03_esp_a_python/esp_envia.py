"""
03 · La ESP32 ENVÍA datos a tu compu                (corre EN la ESP32, MicroPython)

La ESP32 lee dos pines touch y manda una línea de texto por USB cada 50 ms:
    412,398
    405,120      ← aquí alguien tocó el segundo cable
Del otro lado, pc_grafica.py (en tu compu) lee esas líneas y las dibuja.

Este es el esqueleto de casi cualquier proyecto "sensor + visualizador".

Circuito:
    GPIO4  ── cable 1 ── (lo que quieras tocar)
    GPIO27 ── cable 2 ── (lo que quieras tocar)

Instalar como main.py (para que corra solo al encender la tarjeta):
    uv run mpremote cp 03_esp_a_python/esp_envia.py :main.py + reset
Quitarlo después:
    uv run mpremote rm :main.py + reset
"""

import time

from machine import Pin, TouchPad

PINES_TOUCH = [4, 27]          # agrega más pines touch aquí si quieres
sensores = [TouchPad(Pin(numero)) for numero in PINES_TOUCH]

while True:
    lecturas = [str(sensor.read()) for sensor in sensores]
    print(",".join(lecturas))  # formato CSV: fácil de leer del otro lado
    time.sleep_ms(50)
