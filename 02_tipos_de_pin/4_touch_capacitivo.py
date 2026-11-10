"""
02.4 · TOUCH CAPACITIVO — sentir un dedo (o un plátano 🍌)   (corre EN la ESP32)

Algunos pines de la ESP32 miden la CAPACITANCIA de lo que tengan conectado.
Cuando tocas el cable (o algo conductor conectado a él), tu cuerpo agrega
capacitancia y la lectura cambia. Sin botones, sin resistencias.

Circuito:
    GPIO4 ── cable ── (punta libre, papel aluminio, una moneda, una fruta...)

Pines touch de la ESP32 clásica: 4, 27, 32, 33, 14, 13 (evita 0, 2, 12 y 15).

En la ESP32 clásica el valor BAJA al tocar.
(En ESP32-S2 / S3 es al revés: SUBE. Si usas una de esas, cambia el '<' por '>'.)

Correr:
    uv run mpremote run 02_tipos_de_pin/4_touch_capacitivo.py
"""

import time

from machine import Pin, TouchPad

toque = TouchPad(Pin(4))


def calibrar(sensor, muestras=20):
    """Promedia lecturas SIN tocar para saber cuál es el valor 'normal'."""
    suma = 0
    for _ in range(muestras):
        suma += sensor.read()
        time.sleep_ms(50)
    return suma // muestras


print("Calibrando... NO toques el cable")
reposo = calibrar(toque)
umbral = int(reposo * 0.8)          # si baja 20 % o más, lo contamos como toque
print("Reposo:", reposo, " Umbral:", umbral)
print("Ahora sí, toca el cable (Ctrl+C para salir)\n")

while True:
    valor = toque.read()
    tocado = valor < umbral
    print(f"{valor:6d}  {'👆 TOCADO' if tocado else ''}")
    time.sleep_ms(100)
