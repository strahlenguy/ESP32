"""
01 · Hacer parpadear un LED                         (corre EN la ESP32, MicroPython)

Circuito:
    GPIO23 ──[ 220 Ω ]──►|── GND
                        LED
    (pata larga del LED = ánodo, hacia la resistencia; pata corta = cátodo, a GND)

Correr (desde la carpeta raíz del repo):
    uv run mpremote run 01_led_parpadeo/parpadeo.py

Detener: Ctrl+C en la terminal y luego el botón EN (o RST) de la tarjeta.
"""

import time

try:
    from machine import Pin
except ImportError:  # estás en tu compu, no en la ESP32
    raise SystemExit("Este script corre EN la ESP32. Usa:\n"
                     "  uv run mpremote run 01_led_parpadeo/parpadeo.py")

PIN_LED = 23          # LED externo en la protoboard
PIN_LED_PLACA = 2     # LED azul que trae la mayoría de las DevKit
ESPERA = 0.5          # segundos encendido y segundos apagado

led = Pin(PIN_LED, Pin.OUT)
led_placa = Pin(PIN_LED_PLACA, Pin.OUT)

print("Parpadeando en GPIO", PIN_LED, "(Ctrl+C para salir)")

while True:
    led.on()
    led_placa.on()
    time.sleep(ESPERA)

    led.off()
    led_placa.off()
    time.sleep(ESPERA)
