````markdown
# 🛡️ MasterKey Derivator v3.0

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-00c9a0.svg)
![Cryptography](https://img.shields.io/badge/Security-Cryptography-red.svg)

**MasterKey Derivator** es una herramienta de escritorio moderna y segura diseñada para generar contraseñas (claves criptográficas) **determinísticas** a partir de una contraseña maestra y una frase de *salt*. 

En lugar de guardar tus contraseñas en un gestor (donde la base de datos puede ser vulnerada), esta aplicación **calcula** matemáticamente la misma contraseña compleja cada vez que introduces los mismos datos de entrada. Tus claves solo existen en la memoria RAM mientras usas la app.

---

## ✨ Características Principales

* **Interfaz Moderna (Dark Mode):** Construida desde cero con `CustomTkinter` para una experiencia de usuario fluida y visualmente atractiva.
* **Alta Seguridad Criptográfica:** Utiliza algoritmos robustos recomendados por la industria, resistentes a ataques por fuerza bruta con hardware especializado (ASICs/GPUs):
  * *Scrypt* (Recomendado)
  * *PBKDF2-HMAC-SHA512*
  * *SHA3-512 Iterativo*
* **Medidor de Entropía en Tiempo Real:** Evalúa visualmente la fuerza de tu contraseña maestra mientras escribes.
* **Sistema de Contextos:** Genera contraseñas diferentes para distintos sitios (ej. `twitter`, `banco`, `ssh`) usando exactamente las mismas credenciales maestras.
* **Verificación de Claves:** Una pestaña dedicada para comprobar de forma segura que la clave generada coincide con la esperada.

---

## 🚀 Instalación y Uso

Sigue estos pasos para clonar el repositorio y ejecutar la aplicación en tu entorno local.

### 1. Clonar el repositorio

```bash
git clone https://github.com/reimen-cpu/Key-Derivation.git
cd Key-Derivation
````

### 2. Crear un Entorno Virtual (Recomendado)

Para evitar conflictos con otras librerías de tu sistema y el error de "externally-managed-environment":

**En Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**En Windows (PowerShell / CMD):**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install cryptography customtkinter
```

### 4. Ejecutar la aplicación

```bash
python3 Key-Derivation.py
```

*(En Windows puede ser solo `python` en lugar de `python3`).*

---

## 📖 Guía de Uso Rápido

1. **Contraseña Principal:** Ingresa una contraseña maestra fuerte.
2. **Frase de Salt:** Ingresa una segunda frase (salt criptográfico). Debes recordarla; un cambio aunque sea de un carácter genera una clave distinta.
3. **Contexto (Opcional):** Nombre del servicio o propósito de la clave (ej. `facebook`, `vpn-trabajo`) para generar claves únicas.
4. **Configuración:** Elige el algoritmo (recomendado Scrypt), la longitud de la clave y el formato de salida (Base64 recomendado para uso en webs).
5. **Generar Master Key:** Haz clic en el botón y usa "Copiar" para llevarla al portapapeles.

---

## ⚠️ Aviso de Privacidad y Seguridad

Esta aplicación **NO guarda ni transmite ningún dato**. No hay bases de datos, archivos ocultos, telemetría ni conexión a internet. Toda la derivación criptográfica se realiza **localmente en RAM**. Guarda tu contraseña maestra y tu frase de salt de forma segura; sin ellas será imposible regenerar tus claves.

---

**Desarrollado por reimen-cpu**

```
```

