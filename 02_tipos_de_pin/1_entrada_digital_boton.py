"""
02.1 · ENTRADA DIGITAL — un botón                   (corre EN la ESP32, MicroPython)

Una entrada digital solo sabe dos cosas: 1 (hay voltaje) o 0 (no hay).

Circuito:
    GPIO18 ──[ botón ]── GND
    GPIO23 ──[ 220 Ω ]──►|── GND     (el LED de la práctica 01, se queda igual)

No necesitas resistencia para el botón: usamos la resistencia pull-up INTERNA
de la ESP32. Por eso la lógica queda "al revés":
    suelto     → 1  (el pull-up lo jala a 3.3 V)
    presionado → 0  (el botón lo conecta a GND)

Correr:
    uv run mpremote run 02_tipos_de_pin/1_entrada_digital_boton.py
"""

import time

from machine import Pin

boton = Pin(18, Pin.IN, Pin.PULL_UP)
led = Pin(23, Pin.OUT)

anterior = boton.value()
veces = 0

print("Presiona el botón (Ctrl+C para salir)")

while True:
    estado = boton.value()
    led.value(1 - estado)              # LED encendido mientras está presionado

    if estado != anterior:             # solo imprimimos cuando CAMBIA
        if estado == 0:
            veces += 1
            print("Presionado  → total:", veces)
        else:
            print("Suelto")
        anterior = estado

    time.sleep_ms(20)                  # antirrebote sencillo
