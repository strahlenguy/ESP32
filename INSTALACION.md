# Guía de instalación (Windows)

Al terminar esta guía vas a tener:

- tu propia copia de este repo (la **semilla** de tu proyecto final),
- un entorno de Python listo con un solo comando (`uv sync`),
- tu ESP32 detectada y con **MicroPython** instalado.

> **No necesitas instalar Python a mano.** `uv` descarga la versión correcta
> (la que dice el archivo `.python-version`) y todas las librerías del proyecto.

Todos los comandos se escriben en **PowerShell** (búscalo en el menú Inicio).

---

## 0. Lo que necesitas

| Cosa | Nota |
|---|---|
| ESP32 DevKit (ESP32-WROOM-32, 30 o 38 pines) | La más común en tiendas de electrónica |
| Cable USB **de datos** | ⚠️ Muchos cables solo cargan. Si la compu no ve la tarjeta, cambia el cable primero |
| Protoboard, LED, resistencia de 220 Ω, cables dupont | Para la práctica 01 |
| Botón, potenciómetro de 10 kΩ, módulo de micrófono KY-038 | Para la práctica 02 (opcionales) |

Opcional pero recomendado: [VS Code](https://code.visualstudio.com/) con la extensión de Python.

---

## 1. Instala `uv` y `git`

```powershell
winget install --id=astral-sh.uv -e
winget install --id=Git.Git -e
```

<details>
<summary>¿No tienes <code>winget</code>?</summary>

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Y descarga Git desde <https://git-scm.com/download/win>.
</details>

**Cierra PowerShell y ábrelo de nuevo**, y comprueba:

```powershell
uv --version
git --version
```

---

## 2. Instala el driver USB de tu ESP32

Mira el chip pequeño que está junto al conector USB de tu tarjeta:

| El chip dice | Instala |
|---|---|
| CP2102 / CP2104 | *CP210x Universal Windows Driver* (Silicon Labs) |
| CH340 / CH9102 | *CH341SER* (WCH, wch-ic.com) |

Conecta la tarjeta y abre el **Administrador de dispositivos → Puertos (COM y LPT)**.
Debe aparecer algo como `Silicon Labs CP210x ... (COM4)` o `USB-SERIAL CH340 (COM5)`.

---

## 3. Usa este repo como semilla de tu proyecto

**Opción A — GitHub (recomendada):** en la página del repo pulsa
**Use this template → Create a new repository**. Así tienes tu propio repo
desde el primer día. Después clónalo:

```powershell
git clone https://github.com/TU-USUARIO/TU-PROYECTO.git
cd TU-PROYECTO
```

**Opción B — Clonar directo:**

```powershell
git clone https://github.com/strahlenguy/esp32.git mi-proyecto-final
cd mi-proyecto-final
```

Ahora crea el entorno (descarga Python y las librerías; tarda un poco la primera vez):

```powershell
uv sync
```

Desde aquí, **todos los comandos se corren desde la carpeta raíz del repo**
y empiezan con `uv run`, que usa el entorno del proyecto automáticamente.

> Si después necesitas otra librería (por ejemplo para graficar):
> `uv add matplotlib` — se agrega al `pyproject.toml` y tus compañeros solo hacen `uv sync`.

---

## 4. Detecta tu ESP32

Con la tarjeta conectada:

```powershell
uv run python 00_deteccion_esp/windows.py
```

| Resultado | Significa |
|---|---|
| ❌ No encontré ninguna ESP32 | Revisa cable y driver; el script te dice qué hacer |
| 🟡 El puerto abre bien, pero no respondió como MicroPython | **Normal la primera vez.** Sigue al paso 5 |
| ✅ Respondió MicroPython 1.xx | Ya estás listo. Salta a la [práctica 01](01_led_parpadeo/) |

---

## 5. Instala MicroPython en la ESP32 (solo una vez por tarjeta)

```powershell
uv run python firmware/instalar.py
```

El script encuentra tu ESP32, te pide confirmación, borra su memoria, le graba
MicroPython (el `.bin` que viene en la carpeta `firmware/`) y comprueba que funcione.
Si al final dice 🎉 **Listo**, ya puedes pasar a la [práctica 01](01_led_parpadeo/).

**Si falla al grabar** (`Failed to connect` / `Wrong boot mode`): vuelve a correrlo y
mantén presionado el botón **BOOT** de la tarjeta mientras aparece `Connecting....`;
suéltalo cuando empiece a escribir.

---

## 6. Comandos que vas a usar todo el tiempo

| Quiero... | Comando |
|---|---|
| Correr un script en la ESP32 (sin guardarlo) | `uv run mpremote run archivo.py` |
| Abrir la consola de MicroPython (REPL) | `uv run mpremote` → salir con `Ctrl+]` |
| Guardar un script para que corra al encender | `uv run mpremote cp archivo.py :main.py + reset` |
| Ver qué archivos tiene la ESP32 | `uv run mpremote ls` |
| Borrar el `main.py` | `uv run mpremote rm :main.py + reset` |
| Reiniciar la ESP32 | `uv run mpremote reset` (o el botón **EN**) |
| Usar un puerto específico | `uv run mpremote connect COM4 run archivo.py` |

`mpremote` encuentra la ESP32 solo. Si tienes varias tarjetas conectadas, usa `connect COMx`.

> ⚠️ Solo un programa puede usar el puerto a la vez. Si algo dice *Acceso denegado*
> u *ocupado*, cierra Arduino IDE, Thonny, monitores serie u otras terminales con `mpremote`.
