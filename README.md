 # 🛡️ MasterKey Derivator v3.0

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-00c9a0.svg)
![Cryptography](https://img.shields.io/badge/Security-Cryptography-red.svg)

**MasterKey Derivator** es una herramienta de escritorio moderna y segura que te permite generar contraseñas (claves criptográficas) **determinísticas** a partir de una contraseña maestra y una frase de *salt*. 

En lugar de guardar tus contraseñas en un gestor (donde pueden ser hackeadas), esta aplicación **calcula** la misma contraseña compleja cada vez que introduces los mismos datos.

## ✨ Características

* **Interfaz Moderna (Dark Mode):** Construida con `CustomTkinter` para una experiencia fluida y atractiva.
* **Alta Seguridad:** Utiliza algoritmos criptográficos robustos resistentes a ataques por hardware (ASICs/GPUs).
  * *Scrypt* (Recomendado)
  * *PBKDF2-SHA512*
  * *SHA3-512 Iterativo*
* **Medidor de Entropía:** Evalúa visualmente la fuerza de tu contraseña maestra en tiempo real.
* **Sistema de Contextos:** Genera contraseñas diferentes para distintos sitios (ej. `twitter`, `banco`, `ssh`) usando las *mismas* credenciales maestras.
* **Verificación de Claves:** Pestaña dedicada para comprobar que la clave generada coincide con la esperada sin mostrarla accidentalmente en texto plano.

---

## 🚀 Instalación y Uso

Sigue estos pasos para clonar el repositorio y ejecutar la aplicación en tu máquina local.

### 1. Clonar el repositorio
Abre tu terminal y ejecuta:
```bash
git clone https://github.com/TU_USUARIO/Key-Derivation.git
cd Key-Derivation
