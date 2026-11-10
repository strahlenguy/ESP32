"""
02.3 · SALIDA PWM — controlar el brillo de un LED   (corre EN la ESP32, MicroPython)

Una salida digital solo puede ser 0 V o 3.3 V. PWM la prende y apaga muy rápido
(1000 veces por segundo); cambiando qué fracción del tiempo está encendida
(el "ciclo de trabajo" o duty) el LED se ve más o menos brillante.

    duty  0 %   ▁▁▁▁▁▁▁▁▁▁   apagado
    duty 25 %   █▁▁▁█▁▁▁█▁   tenue
    duty 75 %   ███▁███▁██   brillante

Circuito: el mismo de la práctica 01
    GPIO23 ──[ 220 Ω ]──►|── GND

Correr:
    uv run mpremote run 02_tipos_de_pin/3_salida_pwm_brillo_led.py
"""

import time

from machine import PWM, Pin

led = PWM(Pin(23), freq=1000, duty_u16=0)   # duty_u16: 0 (0 %) … 65535 (100 %)
PASO = 1024

print("Respirando... (Ctrl+C para salir)")

while True:
    for brillo in range(0, 65536, PASO):          # sube
        led.duty_u16(brillo)
        time.sleep_ms(10)

    for brillo in range(65535, -1, -PASO):        # baja
        led.duty_u16(brillo)
        time.sleep_ms(10)

# Reto: junta este script con el del potenciómetro para que
# el potenciómetro controle el brillo:  led.duty_u16(pot.read_u16())
