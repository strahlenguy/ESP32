# Guía de instalación

Al terminar esta guía vas a tener:

- tu propia copia de este repo (la **semilla** de tu proyecto final),
- un entorno de Python listo con un solo comando (`uv sync`),
- tu ESP32 detectada y con **MicroPython** instalado.

> **No necesitas instalar Python a mano.** `uv` descarga la versión correcta
> (la que dice el archivo `.python-version`) y todas las librerías del proyecto.
> Así a todos nos funciona igual, en Windows, Linux o Mac.

---

## 0. Lo que necesitas

| Cosa | Nota |
|---|---|
| ESP32 DevKit (ESP32-WROOM-32, 30 o 38 pines) | La más común en tiendas de electrónica |
| Cable USB **de datos** | ⚠️ Muchos cables solo cargan. Si la compu no ve la tarjeta, cambia el cable primero |
| Protoboard, LED, resistencia de 220 Ω, cables dupont | Para la práctica 01 |
| Botón, potenciómetro de 10 kΩ, módulo de micrófono KY-038 | Para la práctica 02 (opcionales) |
| Una terminal | Windows: **PowerShell** · Linux/Mac: **Terminal** |

Opcional pero recomendado: [VS Code](https://code.visualstudio.com/) con la extensión de Python.

---

## 1. Instala `uv` y `git`

Elige tu sistema. Después de instalar, **cierra la terminal y abre una nueva**.

### 🪟 Windows

En **PowerShell**:

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

**Driver USB.** Mira el chip pequeño que está junto al conector USB de tu tarjeta:

| El chip dice | Instala |
|---|---|
| CP2102 / CP2104 | *CP210x Universal Windows Driver* (Silicon Labs) |
| CH340 / CH9102 | *CH341SER* (WCH, wch-ic.com) |

Con la tarjeta conectada, abre el **Administrador de dispositivos → Puertos (COM y LPT)**:
debe aparecer algo como `Silicon Labs CP210x ... (COM4)` o `USB-SERIAL CH340 (COM5)`.

### 🐧 Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
sudo apt install git          # Fedora: sudo dnf install git · Arch: sudo pacman -S git
```

**Permisos del puerto serie** (sin esto verás `Permission denied`):

```bash
sudo usermod -aG dialout $USER     # en Arch/Manjaro el grupo es: uucp
```

Luego **cierra sesión y vuelve a entrar** (o reinicia).

**Solo Ubuntu y derivados:** el paquete `brltty` (lector braille) suele "robarse"
las tarjetas con chip CH340. Si no usas lector braille:

```bash
sudo apt remove brltty
```

### 🍎 macOS

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh     # o: brew install uv
xcode-select --install                               # instala git
```

**Driver USB.** En macOS recientes normalmente no hace falta nada. Si en el paso 3
la tarjeta no aparece, instala el driver de tu chip (CP210x de Silicon Labs o
CH34x de WCH) y autorízalo en **Ajustes del Sistema → Privacidad y seguridad**.

### ✅ Comprueba

```bash
uv --version
git --version
```

---

## 2. Usa este repo como semilla de tu proyecto

**Opción A — GitHub (recomendada):** en la página del repo pulsa
**Use this template → Create a new repository**. Así tienes tu propio repo
desde el primer día. Después clónalo:

```bash
git clone https://github.com/TU-USUARIO/TU-PROYECTO.git
cd TU-PROYECTO
```

**Opción B — Clonar directo:**

```bash
git clone https://github.com/strahlenguy/esp32.git mi-proyecto-final
cd mi-proyecto-final
```

Ahora crea el entorno (descarga Python y las librerías; tarda un poco la primera vez):

```bash
uv sync
```

Eso es todo. Desde aquí, **todos los comandos se corren desde la carpeta raíz del repo**
y empiezan con `uv run`, que usa el entorno del proyecto automáticamente.

> Si después necesitas otra librería (por ejemplo para graficar):
> `uv add matplotlib` — se agrega al `pyproject.toml` y tus compañeros solo hacen `uv sync`.

---

## 3. Detecta tu ESP32

Conecta la tarjeta por USB y corre el script de **tu** sistema:

```bash
uv run python 00_deteccion_esp/windows.py
uv run python 00_deteccion_esp/linux.py
uv run python 00_deteccion_esp/mac.py
```

| Resultado | Significa |
|---|---|
| ❌ No encontré ninguna ESP32 | Revisa cable y driver; el script te dice qué hacer |
| 🟡 El puerto abre bien, pero no respondió como MicroPython | **Normal la primera vez.** Sigue al paso 4 |
| ✅ Respondió MicroPython 1.xx | Ya estás listo. Salta a la [práctica 01](01_led_parpadeo/) |

Anota el puerto que te dice (`COM4`, `/dev/ttyUSB0`, `/dev/cu.usbserial-0001`...).

---

## 4. Instala MicroPython en la ESP32 (solo una vez por tarjeta)

1. Descarga el firmware **ESP32_GENERIC** más reciente (la versión estable, archivo `.bin`) desde
   <https://micropython.org/download/ESP32_GENERIC/>
   y guárdalo en la carpeta `firmware/` de este repo.

2. Borra la memoria de la tarjeta (cambia `PUERTO` por el tuyo):

   ```bash
   uv run esptool --port PUERTO erase-flash
   ```

3. Graba MicroPython (cambia el nombre del archivo por el que descargaste):

   ```bash
   uv run esptool --port PUERTO --baud 460800 write-flash 0x1000 firmware/ESP32_GENERIC-AAAAMMDD-v1.xx.x.bin
   ```

4. Vuelve a correr el script del paso 3. Ahora debe decir ✅ **Respondió MicroPython**.

**Si algo falla al grabar:**

- `Failed to connect` / `Wrong boot mode`: mantén presionado el botón **BOOT** de la
  tarjeta cuando aparezca `Connecting....` y suéltalo cuando empiece a escribir.
- Se corta a la mitad: quita `--baud 460800` (graba más lento pero más seguro).
- ¿Tu tarjeta es ESP32-S3 o C3? Descarga el firmware de esa variante y usa `0x0`
  en lugar de `0x1000`.

---

## 5. Comandos que vas a usar todo el tiempo

| Quiero... | Comando |
|---|---|
| Correr un script en la ESP32 (sin guardarlo) | `uv run mpremote run archivo.py` |
| Abrir la consola de MicroPython (REPL) | `uv run mpremote` → salir con `Ctrl+]` |
| Guardar un script para que corra al encender | `uv run mpremote cp archivo.py :main.py + reset` |
| Ver qué archivos tiene la ESP32 | `uv run mpremote ls` |
| Borrar el `main.py` | `uv run mpremote rm :main.py + reset` |
| Reiniciar la ESP32 | `uv run mpremote reset` (o el botón **EN**) |
| Usar un puerto específico | `uv run mpremote connect PUERTO run archivo.py` |

`mpremote` encuentra la ESP32 solo. Si tienes varias tarjetas conectadas, usa `connect PUERTO`.

> ⚠️ Solo un programa puede usar el puerto a la vez. Si algo dice *busy*, *denegado*
> u *ocupado*, cierra Arduino IDE, Thonny, monitores serie u otras terminales con `mpremote`.
