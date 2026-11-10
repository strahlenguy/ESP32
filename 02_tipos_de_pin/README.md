# 02 · Un ejemplo por tipo de pin

Un pin de la ESP32 puede hacer cosas distintas según cómo lo configures.
Aquí hay **un script por tipo**. Cada uno trae su circuito en el encabezado.

| # | Script | Tipo de pin | Qué necesitas | Pin |
|---|---|---|---|---|
| 1 | `1_entrada_digital_boton.py` | Entrada digital | Botón (+ el LED de la 01) | GPIO18 |
| 2 | `2_entrada_analogica_potenciometro.py` | Entrada analógica (ADC) | Potenciómetro 10 kΩ | GPIO34 |
| 3 | `3_salida_pwm_brillo_led.py` | Salida PWM | El LED de la 01 | GPIO23 |
| 4 | `4_touch_capacitivo.py` | Touch capacitivo | Un cable (¡o un plátano!) | GPIO4 |
| 5 | `5_sensor_de_sonido.py` | Entrada analógica con sensor | Micrófono KY-038 | GPIO35 |

Correr cualquiera:

```bash
uv run mpremote run 02_tipos_de_pin/4_touch_capacitivo.py
```

## Conexiones

```
            ┌──────── ESP32 DevKit ────────┐
   3V3 ─────┤ 3V3                      GND ├───── GND (riel azul −)
            │                              │
 pot. ──────┤ GPIO34 (ADC)    (salida) GPIO23├──[220 Ω]──►|── GND   LED
 micro AO ──┤ GPIO35 (ADC)    (entrada)GPIO18├──[botón]────── GND
            │                              │
 cable ─────┤ GPIO4  (touch)               │
            └──────────────────────────────┘
```

Puedes dejar **todo** conectado a la vez: cada script usa su propio pin.

## Pines que conviene conocer (ESP32 clásica)

| Pines | Para qué | Cuidado |
|---|---|---|
| 4, 13, 14, 16–19, 21–23, 25–27, 32, 33 | Uso general (entrada/salida) | ✅ seguros |
| 32–39 | Entrada analógica (ADC1) | 34–39 son **solo entrada** |
| 4, 13, 14, 27, 32, 33 | Touch capacitivo | ✅ |
| 0, 2, 12, 15 | Afectan el arranque | Evítalos si puedes |
| 6–11 | Memoria flash interna | ❌ No los uses |

**Regla de oro:** los pines trabajan a **3.3 V**. Nunca les metas 5 V.

> Ojo: el ADC2 (pines 0, 2, 4, 12–15, 25–27) no funciona mientras el WiFi está encendido.
> Para lecturas analógicas usa siempre ADC1 (32–39).

## Más ideas de sensores para tu proyecto

| Sensor | Tipo de pin | Idea |
|---|---|---|
| Fotorresistencia (LDR) + resistencia 10 kΩ | ADC | Detectar luz / sombra |
| Sensor de humedad de suelo | ADC | Planta que avisa cuando tiene sed |
| HC-SR04 (ultrasónico) | Digital (2 pines) | Medir distancia |
| DHT11 / DHT22 | Digital (protocolo propio) | Temperatura y humedad |
| Buzzer pasivo | PWM | Hacer música cambiando `freq` |
| Servomotor SG90 | PWM a 50 Hz | Mover algo a un ángulo |
