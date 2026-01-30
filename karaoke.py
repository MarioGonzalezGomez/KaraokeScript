#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from karaoke_core import GestorKaraoke, KaraokeEngine, Cancion
from ipf_service import IPFClient, KaraokeMessages

CONFIG_FILE = "config.json"

class KaraokeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Karaoke Manager & IPF Signaler")
        self.root.geometry("1000x600")
        
        # -- Lógica --
        self.config = self.load_config()
        self.gestor = GestorKaraoke()
        self.engine = KaraokeEngine()
        
        # Red
        self.ipf_client = IPFClient(self.config.get("ipf_ip", "127.0.0.1"), 
                                    self.config.get("ipf_port", 5000))
        self.ipf_builder = KaraokeMessages(self.config.get("ipf_db", "DATABASE"),
                                           self.config.get("karaoke_obj_path", "KARAOKE"))
        
        # Bindings motor
        self.engine.on_progress = self.update_progress
        self.engine.on_lyric = self.send_lyric
        self.engine.on_finish = self.on_song_finish
        
        # Estado
        self.first_line_done = False
        
        # -- UI --
        self.create_ui()
        
        # Cargar lista inicial
        self.refresh_song_list()
    
    # ... (omitted methods) ...

    # --- Acciones motor ---

    def action_play(self):
        self.first_line_done = False
        self.engine.play()

    def action_pause(self):
        self.engine.pause()

    def action_stop(self):
        self.engine.stop()
        self.lbl_live_text.config(text="...")
        self.first_line_done = False
        # Forzar salida si paramos
        self.send_hide()

    def on_song_finish(self):
        self.root.after(0, lambda: messagebox.showinfo("Fin", "Canción terminada"))
        self.send_hide()

    # --- Callbacks del motor (se ejecutan en thread, user after para thread-safety) ---

    def update_progress(self, current_ms, total_ms):
        def _update():
            # Barra
            if total_ms > 0:
                pct = (current_ms / total_ms) * 100
                self.progress_var.set(pct)
            
            # Texto tiempo
            cur_sec = current_ms // 1000
            tot_sec = total_ms // 1000
            self.lbl_time.config(text=f"{cur_sec//60:02d}:{cur_sec%60:02d} / {tot_sec//60:02d}:{tot_sec%60:02d}")
            
        self.root.after(0, _update)

    def send_lyric(self, text):
        def _update():
            # GUI
            self.lbl_live_text.config(text=text)
        
        self.root.after(0, _update)
        
        # IPF Protocol logic
        if not self.first_line_done:
            msg = self.ipf_builder.entra(text)
            self.first_line_done = True
        else:
            msg = self.ipf_builder.cambio(text)
            
        print(f"Sending: {msg}") # Debug
        self.ipf_client.send(msg)

    def send_show(self):
        # Manual show (Entra con texto vacío o prueba)
        msg = self.ipf_builder.entra("PRUEBA DE TEXTO ENTRA")
        self.ipf_client.send(msg)
        
    def send_hide(self):
        msg = self.ipf_builder.sale()
        self.ipf_client.send(msg)

def main():
    root = tk.Tk()
    app = KaraokeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
