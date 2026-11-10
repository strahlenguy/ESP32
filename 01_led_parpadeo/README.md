# 01 · Parpadear un LED

El "hola mundo" de la electrónica: la ESP32 prende y apaga un LED cada medio segundo.

## Circuito

```
   ESP32                      Protoboard
 ┌────────┐
 │  GPIO23├──────[ 220 Ω ]──────┐
 │        │                     │  pata larga (+, ánodo)
 │        │                    ─┴─
 │        │                    ▼   LED
 │        │                    ─┬─
 │        │                     │  pata corta (−, cátodo)
 │     GND├─────────────────────┘
 └────────┘
```

| De | A |
|---|---|
| GPIO23 | Resistencia 220 Ω |
| Resistencia | Pata **larga** del LED |
| Pata **corta** del LED | GND |

**¿Por qué la resistencia?** Limita la corriente. La ESP32 da 3.3 V; un LED rojo
"se come" ~2 V, así que en la resistencia quedan ~1.3 V → I = 1.3 V / 220 Ω ≈ 6 mA.
Sin ella, el LED (o el pin) se puede quemar.

## Correr

```bash
uv run mpremote run 01_led_parpadeo/parpadeo.py
```

También parpadea el LED azul de la tarjeta (GPIO2), así sabes que el código
corre aunque el circuito esté mal.

**Detener:** `Ctrl+C` en la terminal y luego el botón **EN** de la tarjeta.

## Si no prende

1. ¿Parpadea el LED azul de la tarjeta? Si **no**: el problema es la conexión con la compu (vuelve a `00_deteccion_esp`).
2. Si **sí**: el problema está en la protoboard. Voltea el LED (¿pata larga hacia GPIO23?).
3. Revisa que el GND del LED vaya al GND de la ESP32.

## Retos

- Cambia `ESPERA` para que parpadee más rápido.
- Haz que mande "SOS" en código Morse (`··· ——— ···`).
- Agrega un segundo LED en otro pin (25, 26 o 32) y haz que se alternen.
