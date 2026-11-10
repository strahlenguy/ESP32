"""
02.2 · ENTRADA ANALÓGICA (ADC) — un potenciómetro   (corre EN la ESP32, MicroPython)

Una entrada analógica mide CUÁNTO voltaje hay (no solo sí/no).
El ADC convierte 0 – 3.3 V en un número de 0 a 65535.

Circuito (potenciómetro de 10 kΩ, 3 patas):
    pata izquierda ── 3V3
    pata central   ── GPIO34      (el "cursor": su voltaje cambia al girar)
    pata derecha   ── GND

⚠️  Conecta a 3V3, NUNCA a 5V/VIN: más de 3.3 V en un pin puede dañar la ESP32.

Correr:
    uv run mpremote run 02_tipos_de_pin/2_entrada_analogica_potenciometro.py
"""

import time

try:
    from machine import ADC, Pin
except ImportError:  # estás en tu compu, no en la ESP32
    raise SystemExit("Este script corre EN la ESP32. Usa:\n"
                     "  uv run mpremote run 02_tipos_de_pin/2_entrada_analogica_potenciometro.py")

pot = ADC(Pin(34))
pot.atten(ADC.ATTN_11DB)     # rango completo ~0 – 3.3 V

print("Gira el potenciómetro (Ctrl+C para salir)")

while True:
    crudo = pot.read_u16()               # 0 … 65535
    voltaje = crudo * 3.3 / 65535        # aproximado: el ADC de la ESP32 no es perfecto
    porcentaje = crudo * 100 // 65535
    barra = "#" * (porcentaje // 5)      # 20 caracteres = 100 %

    print(f"{crudo:5d}  {voltaje:4.2f} V  |{barra:<20}| {porcentaje:3d} %")
    time.sleep_ms(200)
