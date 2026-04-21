"""
MasterKey Derivator v4.0 (PQC-Grade & Modulable)
Requiere: pip install cryptography customtkinter
"""
import sys
import os
import hashlib
import math
import threading
from tkinter import messagebox
import customtkinter as ctk

# Ensure local imports work correctly (especially important for PyInstaller --onedir / --windowed mode)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from crypto_core.kdf import ALGORITHMS, OUTPUT_FORMATS, KEY_LENGTHS
from utils.clipboard import SecureClipboard

# Configuración global de la interfaz
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

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
    def __init__(self, master, placeholder, show_strength=True, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.show_strength = show_strength
        self.is_hidden = True

        self.entry_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.entry_frame.pack(side="top", fill="x", pady=0)

        self.entry = ctk.CTkEntry(self.entry_frame, placeholder_text=placeholder, show="●", height=38)
        self.entry.pack(side="top", fill="x")
        self.entry.bind("<KeyRelease>", self._update_strength)

        self.toggle_btn = ctk.CTkButton(self.entry_frame, text="👁", width=30, height=30, 
                                        fg_color="transparent", text_color="gray", 
                                        hover_color="#333333", command=self._toggle_visibility)
        self.toggle_btn.place(relx=1.0, rely=0.5, anchor="e", x=-4)

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
        self.title("MasterKey Derivator v4.0")
        self.geometry("750x800")
        self.minsize(600, 750)
        
        self.generated_key = None
        
        self._build_ui()
        
        # Gestor de portapapeles modular estilo KeePass
        self.clipboard_manager = SecureClipboard(self, self._update_status)

    def _build_ui(self):
        self.header = ctk.CTkFrame(self, corner_radius=0, fg_color="#1a1a1a")
        self.header.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(self.header, text="🛡️ MasterKey Derivator", font=("Segoe UI", 20, "bold")).pack(side="left", padx=20, pady=15)
        # Nivel PQC Badge
        ctk.CTkLabel(self.header, text="PQC-Grade", text_color="#22c55e", font=("Segoe UI", 12, "bold")).pack(side="left", pady=15, padx=(0, 10))
        ctk.CTkLabel(self.header, text="v4.0", text_color="gray").pack(side="left", pady=15)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self.tab_derive = self.tabs.add("  Derivar Clave  ")
        self.tab_verify = self.tabs.add("  Verificar  ")

        self.status_lbl = ctk.CTkLabel(self, text="Listo. Ingresa tus credenciales.", text_color="gray", anchor="w")
        self.status_lbl.pack(fill="x", padx=20, pady=(0, 10))

        self._build_derive_tab()
        self._build_verify_tab()

    def _update_status(self, text: str):
        self.status_lbl.configure(text=text)

    def _build_derive_tab(self):
        scroll_frame = ctk.CTkScrollableFrame(self.tab_derive, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        ctk.CTkLabel(scroll_frame, text="CREDENCIALES", font=("Segoe UI", 12, "bold"), text_color="#00c9a0").pack(anchor="w", pady=(10, 5))
        frame_inputs = ctk.CTkFrame(scroll_frame)
        frame_inputs.pack(fill="x", pady=(0, 20))

        self.inp_password = SecureInput(frame_inputs, "Contraseña principal")
        self.inp_password.pack(fill="x", padx=15, pady=(15, 10))

        self.inp_salt = SecureInput(frame_inputs, "Frase de salt (Segunda contraseña)")
        self.inp_salt.pack(fill="x", padx=15, pady=10)

        self.inp_context = ctk.CTkEntry(frame_inputs, placeholder_text="Contexto (ej: wallet-bitcoin, servidor-ssh...)", height=38)
        self.inp_context.pack(fill="x", padx=15, pady=(10, 15))

        ctk.CTkLabel(scroll_frame, text="CONFIGURACIÓN CRIPTOGRÁFICA PQC-GRADE", font=("Segoe UI", 12, "bold"), text_color="#00c9a0").pack(anchor="w", pady=(0, 5))
        frame_config = ctk.CTkFrame(scroll_frame)
        frame_config.pack(fill="x", pady=(0, 20))

        grid = ctk.CTkFrame(frame_config, fg_color="transparent")
        grid.pack(fill="x", padx=15, pady=15)
        grid.columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(grid, text="Algoritmo:", anchor="w").grid(row=0, column=0, sticky="w", padx=5)
        self.cb_algo = ctk.CTkOptionMenu(grid, values=list(ALGORITHMS.keys()))
        self.cb_algo.set("Scrypt (Recomendado PQC-grade)") # Default post-quantum seguro
        self.cb_algo.grid(row=1, column=0, sticky="ew", padx=5, pady=(0, 10))

        ctk.CTkLabel(grid, text="Longitud:", anchor="w").grid(row=0, column=1, sticky="w", padx=5)
        self.cb_length = ctk.CTkOptionMenu(grid, values=list(KEY_LENGTHS.keys()))
        self.cb_length.set("256 bits (32 B - Nivel PQC 1)") # Default 256 bits para Grover
        self.cb_length.grid(row=1, column=1, sticky="ew", padx=5, pady=(0, 10))

        ctk.CTkLabel(grid, text="Formato:", anchor="w").grid(row=0, column=2, sticky="w", padx=5)
        self.cb_format = ctk.CTkOptionMenu(grid, values=list(OUTPUT_FORMATS.keys()))
        self.cb_format.grid(row=1, column=2, sticky="ew", padx=5, pady=(0, 10))

        self.btn_derive = ctk.CTkButton(scroll_frame, text="GENERAR MASTER KEY", font=("Segoe UI", 14, "bold"), 
                                        height=45, fg_color="#00c9a0", hover_color="#009977", text_color="black",
                                        command=self._start_derivation)
        self.btn_derive.pack(fill="x", pady=(0, 5))
        
        ctk.CTkButton(scroll_frame, text="Limpiar campos", fg_color="transparent", text_color="gray", 
                      hover_color="#333", command=self._clear_all).pack(pady=(0, 20))

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

        self.btn_derive.configure(state="disabled", text="Derivando (esto toma tiempo)...", fg_color="gray")
        self._update_status("Procesando criptografía intensiva...")
        
        threading.Thread(target=self._process_derivation, args=(pw, salt, ctx, algo, length, fmt), daemon=True).start()

    def _process_derivation(self, pw, salt, ctx, algo_name, length, fmt_name):
        try:
            key = ALGORITHMS[algo_name](pw, salt, ctx, length)
            formatted_key = OUTPUT_FORMATS[fmt_name](key)
            fingerprint = hashlib.sha256(key).hexdigest()[:40]

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
        self._update_status("✅ Clave generada exitosamente.")
        self.lbl_verify_res.configure(text="")

    def _handle_error(self, error_msg):
        self.btn_derive.configure(state="normal", text="GENERAR MASTER KEY", fg_color="#00c9a0")
        self._update_status("❌ Error durante la derivación.")
        messagebox.showerror("Error criptográfico", error_msg)

    # ══════════════════════════════════════════════════════
    #  DELEGACIÓN DE PORTAPAPELES
    # ══════════════════════════════════════════════════════

    def _copy_to_clipboard(self):
        text = self.txt_output.get("1.0", "end").strip()
        if text:
            self.clipboard_manager.copy_sensitive_data(text)

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
        
        # Detener la cuenta de portapapeles y forzar el borrado de seguridad
        self.clipboard_manager.stop_and_clear_immediately()
        
        self._update_status("Campos limpiados.")

if __name__ == "__main__":
    app = ModernApp()
    app.mainloop()
