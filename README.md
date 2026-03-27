# 🛡️ MasterKey Derivator v3.0

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-00c9a0.svg)
![Cryptography](https://img.shields.io/badge/Security-Cryptography-red.svg)

**MasterKey Derivator** is a modern and secure desktop tool designed to generate **deterministic** passwords (cryptographic keys) from a master password and a *salt* phrase.

Instead of storing your passwords in a manager (where the database can be compromised), this application **mathematically computes** the same complex password every time you enter the same input data. Your keys only exist in RAM while using the app.

---

## ✨ Key Features

* **Modern Interface (Dark Mode):** Built from scratch with `CustomTkinter` for a smooth and visually appealing user experience.
* **High Cryptographic Security:** Uses industry-recommended robust algorithms, resistant to brute-force attacks with specialized hardware (ASICs/GPUs):
  * *Scrypt* (Recommended)
  * *PBKDF2-HMAC-SHA512*
  * *Iterative SHA3-512*
* **Real-Time Entropy Meter:** Visually evaluates the strength of your master password as you type.
* **Context System:** Generates different passwords for different sites (e.g., `twitter`, `bank`, `ssh`) using exactly the same master credentials.
* **Key Verification:** A dedicated tab to securely check that the generated key matches the expected one.

---

## 🚀 Installation and Usage

Follow these steps to clone the repository and run the application locally.

### 1. Clone the repository

```bash
git clone https://github.com/reimen-cpu/Key-Derivation.git
cd Key-Derivation
````

### 2. Create a Virtual Environment (Recommended)

To avoid conflicts with other libraries on your system and the "externally-managed-environment" error:

**On Linux / macOS:**

```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows (PowerShell / CMD):**

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

With the virtual environment activated:

```bash
pip install cryptography customtkinter
```

### 4. Run the application

```bash
python3 Key-Derivation.py
```

*(On Windows, `python` may be sufficient instead of `python3`).*

---

## 📖 Quick Usage Guide

1. **Master Password:** Enter a strong master password.
2. **Salt Phrase:** Enter a second phrase (cryptographic salt). You must remember it; even a single-character change produces a completely different key.
3. **Context (Optional):** Name the service or purpose of the key (e.g., `facebook`, `vpn-work`) to generate unique keys for each.
4. **Settings:** Choose the algorithm (Scrypt recommended), key length, and output format (Base64 recommended for web use).
5. **Generate Master Key:** Click the button and use "Copy" to place it in your clipboard.

---

## ⚠️ Privacy and Security Notice

This application **does NOT store or transmit any data**. There are no databases, hidden files, telemetry, or internet connections. All cryptographic derivation is performed **locally in RAM**. Keep your master password and salt phrase secure; without them, regenerating your keys is mathematically impossible.

---

**Developed by reimen-cpu**

