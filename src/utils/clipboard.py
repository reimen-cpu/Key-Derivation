"""
utils.clipboard
===============
Manejo seguro del portapapeles del sistema para prevenir filtración de datos.
Implementa una limpieza automática temporal estilo KeePass.
"""

from typing import Callable, Any

class SecureClipboard:
    """
    Gestor del portapapeles temporal (autoborrado de seguridad) que interactúa
    limpiamente con la ventana root de CustomTkinter/Tkinter.
    """
    
    def __init__(self, root: Any, status_callback: Callable[[str], None]):
        """
        :param root: Instancia de CustomTkinter / Tk
        :param status_callback: Función para actualizar el status_lbl con mensajes string.
        """
        self.root = root
        self.status_callback = status_callback
        
        self._clipboard_timer = None
        self._last_copied_text = None
        self._countdown = 0

    def copy_sensitive_data(self, text: str):
        """
        Copia texto al portapapeles y configura el autoborrado seguro a 15 segundos.
        Las instancias previas del temporizador son canceladas.
        """
        if not text:
            return
            
        # 1. Cancelar temporizador previo si existe
        if self._clipboard_timer is not None:
            self.root.after_cancel(self._clipboard_timer)
            
        # 2. Forzar el copiado al sistema operativo
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update() # IMPORTANTE: Obliga a X11/Wayland a registrar el cambio
        
        # 3. Guardar el estado exacto para luego verificar
        self._last_copied_text = text
        self._countdown = 15
        
        # 4. Iniciar el loop visual del temporizador
        self._update_countdown()

    def stop_and_clear_immediately(self):
        """Cancela la cuenta regresiva existente y borra el portapapeles inmediatamente sin esperar."""
        if self._clipboard_timer is not None:
            self.root.after_cancel(self._clipboard_timer)
            self._countdown = 0
            self._auto_clear()

    def _update_countdown(self):
        """Loop asíncrono en la UI que actualiza 1 vez por segundo usando root.after()"""
        if self._countdown > 0:
            self.status_callback(f"📋 Clave copiada. Borrando portapapeles en {self._countdown}s...")
            self._countdown -= 1
            self._clipboard_timer = self.root.after(1000, self._update_countdown)
        else:
            self._auto_clear()

    def _auto_clear(self):
        """
        Lógica KeePass: Solo borra el portapapeles si NO ha sido modificado 
        por el usuario mientras tanto. Sobrescribe la memoria localmente con un string vacío.
        """
        try:
            current_clipboard = self.root.clipboard_get()
            
            if current_clipboard == self._last_copied_text:
                self.root.clipboard_clear()
                self.root.clipboard_append("") # Sobrescribir elimina vestigios ("fantasmas")
                self.root.update()             # Forza a gestores como Klipper del SO a limpiar
                self.status_callback("🗑️ Portapapeles borrado por seguridad.")
            else:
                self.status_callback("ℹ️ El portapapeles cambió. No se borró el nuevo contenido.")
                
        except Exception:
            # clipboard_get() lanza error interno en Tkinter si está totalmente vacío
            self.status_callback("🗑️ El portapapeles ya estaba vacío.")
        finally:
            self._clipboard_timer = None
            self._last_copied_text = None
