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
        
        # -- UI --
        self.create_ui()
        
        # Cargar lista inicial
        self.refresh_song_list()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)

    def create_ui(self):
        # Estilos
        style = ttk.Style()
        style.configure("Big.TLabel", font=("Arial", 24, "bold"))
        style.configure("Medium.TLabel", font=("Arial", 14))
        
        # --- Sidebar (Izquierda) ---
        sidebar = ttk.Frame(self.root, width=250, padding="10")
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        
        ttk.Label(sidebar, text="Canciones", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_songs)
        ttk.Entry(sidebar, textvariable=self.search_var).pack(fill=tk.X, pady=5)
        
        self.listbox = tk.Listbox(sidebar)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_song)
        
        ttk.Button(sidebar, text="Recargar", command=self.refresh_song_list).pack(fill=tk.X, pady=5)

        # --- Main Area (Derecha) ---
        main_area = ttk.Frame(self.root, padding="20")
        main_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Header / Status
        header_frame = ttk.Frame(main_area)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.lbl_status = tk.Label(header_frame, text="Desconectado", fg="red", font=("Arial", 10, "bold"))
        self.lbl_status.pack(side=tk.RIGHT)
        
        ttk.Label(header_frame, text="IPF Control", font=("Arial", 16, "bold")).pack(side=tk.LEFT)
        
        # info canción
        self.lbl_song_title = ttk.Label(main_area, text="Seleccione una canción", style="Big.TLabel", justify=tk.CENTER)
        self.lbl_song_title.pack(pady=10)
        
        self.lbl_song_artist = ttk.Label(main_area, text="-", style="Medium.TLabel")
        self.lbl_song_artist.pack(pady=5)
        
        # Teleprompter Area
        prompter_frame = ttk.LabelFrame(main_area, text="Salida en Vivo", padding="20")
        prompter_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        self.lbl_live_text = tk.Label(prompter_frame, text="...", font=("Arial", 28), wraplength=600, fg="#333")
        self.lbl_live_text.pack(expand=True)
        
        # Progress
        progress_frame = ttk.Frame(main_area)
        progress_frame.pack(fill=tk.X, pady=10)
        
        self.lbl_time = ttk.Label(progress_frame, text="00:00 / 00:00")
        self.lbl_time.pack(side=tk.RIGHT)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        # Controls
        controls_frame = ttk.Frame(main_area)
        controls_frame.pack(fill=tk.X, pady=10)
        
        self.btn_play = ttk.Button(controls_frame, text="▶ PLAY", command=self.action_play, state=tk.DISABLED)
        self.btn_play.pack(side=tk.LEFT, padx=5)
        
        self.btn_pause = ttk.Button(controls_frame, text="⏸ PAUSE", command=self.action_pause, state=tk.DISABLED)
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        
        self.btn_stop = ttk.Button(controls_frame, text="⏹ STOP", command=self.action_stop, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=5)
        
        # Connection Panel
        conn_frame = ttk.LabelFrame(main_area, text="Configuración Conexión", padding="10")
        conn_frame.pack(fill=tk.X, pady=20)
        
        ttk.Label(conn_frame, text="IP:").pack(side=tk.LEFT)
        self.entry_ip = ttk.Entry(conn_frame, width=15)
        self.entry_ip.insert(0, self.config.get("ipf_ip", "127.0.0.1"))
        self.entry_ip.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(conn_frame, text="Puerto:").pack(side=tk.LEFT)
        self.entry_port = ttk.Entry(conn_frame, width=8)
        self.entry_port.insert(0, str(self.config.get("ipf_port", 5000)))
        self.entry_port.pack(side=tk.LEFT, padx=5)
        
        self.btn_connect = ttk.Button(conn_frame, text="Conectar", command=self.toggle_connection)
        self.btn_connect.pack(side=tk.LEFT, padx=20)
        
        # Commands manuales
        ttk.Button(conn_frame, text="Mostrar Gráfico", command=self.send_show).pack(side=tk.RIGHT, padx=5)
        ttk.Button(conn_frame, text="Ocultar Gráfico", command=self.send_hide).pack(side=tk.RIGHT, padx=5)

    # --- Lógica de UI ---

    def refresh_song_list(self):
        self.gestor.cargar_canciones()
        self.filter_songs()

    def filter_songs(self, *args):
        query = self.search_var.get()
        canciones = self.gestor.buscar(query)
        self.listbox.delete(0, tk.END)
        for c in canciones:
            self.listbox.insert(tk.END, f"{c.titulo} - {c.artista}")
    
    def on_select_song(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        # Buscar objeto canción correspondiente
        # Nota: Esto asume que el orden filtrado coincide con buscar. 
        # Para ser más robusto deberíamos guardar una referencia oculta, 
        # pero por simplicidad volvemos a buscar en el gestor la lista filtrada.
        query = self.search_var.get()
        canciones_filtradas = self.gestor.buscar(query)
        
        if selection[0] < len(canciones_filtradas):
            cancion = canciones_filtradas[selection[0]]
            self.engine.load_song(cancion)
            
            self.lbl_song_title.config(text=cancion.titulo)
            self.lbl_song_artist.config(text=cancion.artista)
            self.lbl_live_text.config(text="Preparado...")
            self.progress_var.set(0)
            self.update_progress(0, cancion.duracion)
            
            self.btn_play.config(state=tk.NORMAL)
            self.btn_pause.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.NORMAL)

    def toggle_connection(self):
        if not self.ipf_client.connected:
            # Conectar
            ip = self.entry_ip.get()
            try:
                port = int(self.entry_port.get())
            except:
                messagebox.showerror("Error", "Puerto inválido")
                return
            
            # Guardar config
            self.config["ipf_ip"] = ip
            self.config["ipf_port"] = port
            self.save_config()
            
            # Actualizar cliente
            self.ipf_client.ip = ip
            self.ipf_client.port = port
            
            if self.ipf_client.connect():
                self.lbl_status.config(text="Conectado", fg="green")
                self.btn_connect.config(text="Desconectar")
            else:
                messagebox.showerror("Error", "No se pudo conectar a IPF")
        else:
            # Desconectar
            self.ipf_client.disconnect()
            self.lbl_status.config(text="Desconectado", fg="red")
            self.btn_connect.config(text="Conectar")

    # --- Acciones motor ---

    def action_play(self):
        self.engine.play()

    def action_pause(self):
        self.engine.pause()

    def action_stop(self):
        self.engine.stop()
        self.lbl_live_text.config(text="...")
        self.send_lyric("") # Limpiar pantalla IPF

    def on_song_finish(self):
        self.root.after(0, lambda: messagebox.showinfo("Fin", "Canción terminada"))

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
        
        # IPF (Enviar directamente)
        msg = self.ipf_builder.set_texto(text)
        print(f"Sending: {msg}") # Debug
        self.ipf_client.send(msg)

    def send_show(self):
        msg = self.ipf_builder.mostrar()
        self.ipf_client.send(msg)
        
    def send_hide(self):
        msg = self.ipf_builder.ocultar()
        self.ipf_client.send(msg)

def main():
    root = tk.Tk()
    app = KaraokeApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
