"""
MasterKey Derivator v3.0 (Modernizado)
Requiere: pip install cryptography customtkinter
"""

import hashlib
import hmac
import math
import base64
import threading
import customtkinter as ctk
from tkinter import messagebox

from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

# Configuración global de la interfaz
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# ══════════════════════════════════════════════════════
#  CRIPTOGRAFÍA (Lógica separada y limpia)
# ══════════════════════════════════════════════════════

def _fixed_salt(context: str, salt_phrase: str) -> bytes:
    key = salt_phrase.encode("utf-8")
    msg = context.encode("utf-8") if context else b"masterkey-derivator-v2"
    return hmac.new(key, msg, hashlib.sha256).digest()

def derive_scrypt(password: str, salt_phrase: str, context: str, length: int) -> bytes:
    salt = _fixed_salt(context, salt_phrase)
    kdf = Scrypt(salt=salt, length=length, n=2**15, r=8, p=1, backend=default_backend())
    return kdf.derive(password.encode("utf-8"))

def derive_pbkdf2(password: str, salt_phrase: str, context: str, length: int) -> bytes:
    salt = _fixed_salt(context, salt_phrase)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA512(), length=length,
                     salt=salt, iterations=600_000, backend=default_backend())
    return kdf.derive(password.encode("utf-8"))

def derive_sha3(password: str, salt_phrase: str, context: str, length: int) -> bytes:
    salt = _fixed_salt(context, salt_phrase)
    data = password.encode("utf-8") + salt
    for _ in range(200_000):
        data = hashlib.sha3_512(data).digest()
    return data[:length]

ALGORITHMS = {
    "Scrypt (Recomendado)": derive_scrypt,
    "PBKDF2-SHA512": derive_pbkdf2,
    "SHA3-512 iterativo": derive_sha3,
}

OUTPUT_FORMATS = {
    "Hexadecimal": lambda b: b.hex(),
    "Base64": lambda b: base64.b64encode(b).decode(),
    "Base64 URL-safe": lambda b: base64.urlsafe_b64encode(b).decode(),
}

KEY_LENGTHS = {
    "128 bits (16 B)": 16,
    "192 bits (24 B)": 24,
    "256 bits (32 B)": 32,
    "512 bits (64 B)": 64,
}

def calc_entropy(pw: str) -> float:
    if not pw: return 0.0
    cs = 0
    if any(c.islower() for c in pw): cs += 26
    if any(c.isupper() for c in pw): cs += 26
    if any(c.isdigit() for c in pw): cs += 10
    if any(not c.isalnum() for c in pw): cs += 32
    return len(pw) * math.log2(cs or 26)


# ══════════════════════════════════════════════════════
#  WIDGETS PERSONALIZADOS
# ══════════════════════════════════════════════════════

class SecureInput(ctk.CTkFrame):
    """Un campo de contraseña moderno con botón para mostrar/ocultar y medidor de fuerza."""
    def __init__(self, master, placeholder, show_strength=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_strength = show_strength
        self.is_hidden = True

        # Contenedor para el Entry y el Botón
        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.pack(side="top", fill="x", pady=0)

        # Input Field
        self.entry = ctk.CTkEntry(self.entry_frame, placeholder_text=placeholder, show="●", height=38)
        self.entry.pack(side="top", fill="x")
        self.entry.bind("<KeyRelease>", self._update_strength)

        # Show/Hide Button (Flotando a la derecha sobre el Entry usando "place")
        self.toggle_btn = ctk.CTkButton(self.entry_frame, text="👁", width=30, height=30, 
                                        fg_color="transparent", text_color="gray", 
                                        hover_color="#333333", command=self._toggle_visibility)
        self.toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-4)

        # Strength Bar
        if self.show_strength:
            self.bar_frame = ctk.CTkFrame(self, fg_color="transparent")
            self.bar_frame.pack(side="top", fill="x", pady=(5, 0))
            
            self.progress = ctk.CTkProgressBar(self.bar_frame, height=4, progress_color="gray")
            self.progress.pack(side="left", fill="x", expand=True)
            self.progress.set(0)
            
            self.lbl_strength = ctk.CTkLabel(self.bar_frame, text="", text_color="gray", 
                                             font=("Segoe UI", 11), width=80, anchor="e")
            self.lbl_strength.pack(side="right", padx=(10, 0))

    def _toggle_visibility(self):
        self.is_hidden = not self.is_hidden
        self.entry.configure(show="●" if self.is_hidden else "")
        self.toggle_btn.configure(text_color="gray" if self.is_hidden else "white")

    def _update_strength(self, event=None):
        if not self.show_strength: return
        pw = self.entry.get()
        if not pw:
            self.progress.set(0)
            self.lbl_strength.configure(text="", text_color="gray")
            return

        e = calc_entropy(pw)
        if e < 25:   r, col, lbl = 0.2, "#ef4444", "Muy débil"
        elif e < 40: r, col, lbl = 0.4, "#f97316", "Débil"
        elif e < 60: r, col, lbl = 0.6, "#f59e0b", "Moderada"
        elif e < 80: r, col, lbl = 0.8, "#00c9a0", "Fuerte"
        else:        r, col, lbl = 1.0, "#22c55e", "Muy fuerte"

        self.progress.set(r)
        self.progress.configure(progress_color=col)
        self.lbl_strength.configure(text=lbl, text_color=col)

    def get(self):
        return self.entry.get().strip()

    def clear(self):
        self.entry.delete(0, 'end')
        self._update_strength()


# ══════════════════════════════════════════════════════
#  APLICACIÓN PRINCIPAL
# ══════════════════════════════════════════════════════

class ModernApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MasterKey Derivator v3.0")
        self.geometry("750x800")
        self.minsize(600, 750)
        self.generated_key = None

        self._build_ui()

    def _build_ui(self):
        # --- HEADER ---
        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        self.header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.header, text="🛡️ MasterKey Derivator", font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=15)
        ctk.CTkLabel(self.header, text="v3.0", text_color="gray").pack(side="left", pady=15)

        # --- TABS ---
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_derive = self.tabs.add("  Derivar Clave  ")
        self.tab_verify = self.tabs.add("  Verificar  ")

        self._build_derive_tab()
        self._build_verify_tab()

        # --- STATUS BAR ---
        self.status_lbl = ctk.CTkLabel(self, text="Listo. Ingresa tus credenciales.", text_color="gray", anchor="w")
        self.status_lbl.pack(fill="x", padx=20, pady=(0, 10))

    def _build_derive_tab(self):
        # Scrollable Frame for deriving
        scroll_frame = ctk.CTkScrollableFrame(self.tab_derive, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        # 1. ENTRADAS
        ctk.CTkLabel(scroll_frame, text="CREDENCIALES", font=("Segoe UI", 12, "bold"), text_color="#00c9a0").pack(anchor="w", pady=(10, 5))
        frame_inputs = ctk.CTkFrame(scroll_frame)
        frame_inputs.pack(fill="x", pady=(0, 20))

        self.inp_password = SecureInput(frame_inputs, "Contraseña principal")
        self.inp_password.pack(fill="x", padx=15, pady=(15, 10))

        self.inp_salt = SecureInput(frame_inputs, "Frase de salt (Segunda contraseña)")
        self.inp_salt.pack(fill="x", padx=15, pady=10)

        self.inp_context = ctk.CTkEntry(frame_inputs, placeholder_text="Contexto (ej: wallet-bitcoin, servidor-ssh...)", height=38)
        self.inp_context.pack(fill="x", padx=15, pady=(10, 15))

        # 2. CONFIGURACIÓN
        ctk.CTkLabel(scroll_frame, text="CONFIGURACIÓN CRIPTOGRÁFICA", font=("Segoe UI", 12, "bold"), text_color="#00c9a0").pack(anchor="w", pady=(0, 5))
        frame_config = ctk.CTkFrame(scroll_frame)
        frame_config.pack(fill="x", pady=(0, 20))

        grid = ctk.CTkFrame(frame_config, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=15)
        grid.columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(grid, text="Algoritmo:", anchor="w").grid(row=0, column=0, sticky="w", padx=5)
        self.cb_algo = ctk.CTkOptionMenu(grid, values=list(ALGORITHMS.keys()))
        self.cb_algo.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))

        ctk.CTkLabel(grid, text="Longitud:", anchor="w").grid(row=0, column=1, sticky="w", padx=5)
        self.cb_length = ctk.CTkOptionMenu(grid, values=list(KEY_LENGTHS.keys()))
        self.cb_length.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))

        ctk.CTkLabel(grid, text="Formato:", anchor="w").grid(row=0, column=2, sticky="w", padx=5)
        self.cb_format = ctk.CTkOptionMenu(grid, values=list(OUTPUT_FORMATS.keys()))
        self.cb_format.grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 10))

        # 3. ACCIÓN
        self.btn_derive = ctk.CTkButton(scroll_frame, text="GENERAR MASTER KEY", font=("Segoe UI", 14, "bold"), 
                                        height=45, fg_color="#00c9a0", hover_color="#009977", text_color="black",
                                        command=self._start_derivation)
        self.btn_derive.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(scroll_frame, text="Limpiar campos", fg_color="transparent", text_color="gray", 
                      hover_color="#333", command=self._clear_all).pack(pady=(0, 20))

        # 4. RESULTADO
        ctk.CTkLabel(scroll_frame, text="RESULTADO", font=("Segoe UI", 12, "bold"), text_color="#00c9a0").pack(anchor="w", pady=(0, 5))
        self.frame_result = ctk.CTkFrame(scroll_frame, border_width=1, border_color="#00c9a0", fg_color="#0a1520")
        self.frame_result.pack(fill="x", pady=(0, 10))

        top_res = ctk.CTkFrame(self.frame_result, fg_color="transparent")
        top_res.pack(fill="x", padx=10, pady=(10, 5))
        
        self.lbl_badges = ctk.CTkLabel(top_res, text="", font=("Segoe UI", 12, "bold"))
        self.lbl_badges.pack(side="left")

        ctk.CTkButton(top_res, text="Copiar", width=60, height=24, fg_color="#1d4ed8", 
                      command=self._copy_to_clipboard).pack(side="right")

        self.txt_output = ctk.CTkTextbox(self.frame_result, height=80, font=("Courier New", 14), 
                                         text_color="#4ade80", fg_color="transparent", state="disabled")
        self.txt_output.pack(fill="x", padx=10, pady=(0, 10))

        self.lbl_fp = ctk.CTkLabel(self.frame_result, text="SHA-256 Fingerprint: --", font=("Courier New", 11), text_color="gray")
        self.lbl_fp.pack(anchor="w", padx=15, pady=(0, 10))

    def _build_verify_tab(self):
        ctk.CTkLabel(self.tab_verify, text="VERIFICACIÓN DE CLAVE", font=("Segoe UI", 16, "bold")).pack(pady=(20, 10))
        ctk.CTkLabel(self.tab_verify, text="Pega aquí una clave generada para comprobar si coincide con los datos actuales.", 
                     text_color="gray", wraplength=500).pack(pady=(0, 20))

        self.inp_verify = ctk.CTkEntry(self.tab_verify, placeholder_text="Pega la clave aquí...", font=("Courier New", 13), height=40)
        self.inp_verify.pack(fill="x", padx=40, pady=10)

        self.btn_verify = ctk.CTkButton(self.tab_verify, text="Verificar Coincidencia", height=40, command=self._verify_key)
        self.btn_verify.pack(pady=20)

        self.lbl_verify_res = ctk.CTkLabel(self.tab_verify, text="", font=("Segoe UI", 16, "bold"))
        self.lbl_verify_res.pack(pady=10)

    # ══════════════════════════════════════════════════════
    #  LÓGICA DE INTERACCIÓN
    # ══════════════════════════════════════════════════════

    def _start_derivation(self):
        pw = self.inp_password.get()
        salt = self.inp_salt.get()
        ctx = self.inp_context.get().strip()
        algo = self.cb_algo.get()
        length = KEY_LENGTHS[self.cb_length.get()]
        fmt = self.cb_format.get()

        if not pw or not salt:
            messagebox.showwarning("Faltan datos", "La contraseña principal y la frase de salt son obligatorias.")
            return

        # UI Update for loading state
        self.btn_derive.configure(state="disabled", text="Derivando (esto toma tiempo)...", fg_color="gray")
        self.status_lbl.configure(text="Procesando criptografía intensiva...")
        
        # Run in thread to not freeze UI
        threading.Thread(target=self._process_derivation, args=(pw, salt, ctx, algo, length, fmt), daemon=True).start()

    def _process_derivation(self, pw, salt, ctx, algo_name, length, fmt_name):
        try:
            key = ALGORITHMS[algo_name](pw, salt, ctx, length)
            formatted_key = OUTPUT_FORMATS[fmt_name](key)
            fingerprint = hashlib.sha256(key).hexdigest()[:40]

            # Return to main thread to update UI
            self.after(0, self._update_ui_with_key, key, formatted_key, fingerprint, algo_name, length)
        except Exception as e:
            self.after(0, self._handle_error, str(e))

    def _update_ui_with_key(self, raw_key, formatted_key, fingerprint, algo_name, length):
        self.generated_key = raw_key

        self.txt_output.configure(state="normal")
        self.txt_output.delete("1.0", "end")
        self.txt_output.insert("1.0", formatted_key)
        self.txt_output.configure(state="disabled")

        self.lbl_badges.configure(text=f" {algo_name.split()[0]} | {length*8} bits ")
        self.lbl_fp.configure(text=f"SHA-256 Fingerprint: {fingerprint}...")

        self.btn_derive.configure(state="normal", text="GENERAR MASTER KEY", fg_color="#00c9a0")
        self.status_lbl.configure(text="✅ Clave generada exitosamente.")
        self.lbl_verify_res.configure(text="") # Clear verify tab

    def _handle_error(self, error_msg):
        self.btn_derive.configure(state="normal", text="GENERAR MASTER KEY", fg_color="#00c9a0")
        self.status_lbl.configure(text="❌ Error durante la derivación.")
        messagebox.showerror("Error criptográfico", error_msg)

    def _copy_to_clipboard(self):
        text = self.txt_output.get("1.0", "end").strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_lbl.configure(text="📋 Clave copiada al portapapeles.")

    def _verify_key(self):
        if not self.generated_key:
            self.lbl_verify_res.configure(text="Deriva una clave primero.", text_color="orange")
            return
        
        candidate = self.inp_verify.get().strip()
        expected = OUTPUT_FORMATS[self.cb_format.get()](self.generated_key)

        if candidate == expected:
            self.lbl_verify_res.configure(text="✅ LAS CLAVES COINCIDEN", text_color="#22c55e")
        else:
            self.lbl_verify_res.configure(text="❌ LAS CLAVES NO COINCIDEN", text_color="#ef4444")

    def _clear_all(self):
        self.inp_password.clear()
        self.inp_salt.clear()
        self.inp_context.delete(0, 'end')
        
        self.txt_output.configure(state="normal")
        self.txt_output.delete("1.0", "end")
        self.txt_output.configure(state="disabled")
        
        self.lbl_badges.configure(text="")
        self.lbl_fp.configure(text="SHA-256 Fingerprint: --")
        self.generated_key = None
        self.status_lbl.configure(text="Campos limpiados.")

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
