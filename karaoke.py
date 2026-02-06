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
        self.engine.on_clear = self.send_hide_event # Handler para limpiar texto
        self.engine.on_finish = self.on_song_finish
        
        # Estado
        self.first_line_done = False
        
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
        # Notebook (Pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña Reproductor
        self.tab_player = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_player, text="Reproductor")
        self.create_player_tab(self.tab_player)
        
        # Pestaña Sincronizador
        self.tab_sync = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_sync, text="Sincronizador")
        self.create_sync_tab(self.tab_sync)

    def create_player_tab(self, parent):
        # Estilos
        style = ttk.Style()
        style.configure("Big.TLabel", font=("Arial", 24, "bold"))
        style.configure("Medium.TLabel", font=("Arial", 14))
        
        # Layout Resizable (PanedWindow)
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # --- Sidebar (Izquierda) ---
        sidebar = ttk.Frame(paned, width=300, padding="10")
        paned.add(sidebar, weight=1)
        
        ttk.Label(sidebar, text="Canciones", font=("Arial", 12, "bold")).pack(pady=5)
        
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_songs)
        ttk.Entry(sidebar, textvariable=self.search_var).pack(fill=tk.X, pady=5)
        
        self.listbox = tk.Listbox(sidebar)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.listbox.bind('<<ListboxSelect>>', self.on_select_song)
        
        ttk.Button(sidebar, text="Recargar", command=self.refresh_song_list).pack(fill=tk.X, pady=5)

        # --- Main Area (Derecha) ---
        main_area = ttk.Frame(paned, padding="20")
        paned.add(main_area, weight=4)
        
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

    def create_sync_tab(self, parent):
        # Layout: Izquierda (Lista canciones), Derecha (Tabla y Edición)
        paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # --- Sidebar Sync (Lista) ---
        frame_list = ttk.Frame(paned, width=200)
        paned.add(frame_list, weight=1)
        
        ttk.Label(frame_list, text="Seleccionar Canción").pack(pady=5)
        self.sync_listbox = tk.Listbox(frame_list)
        self.sync_listbox.pack(fill=tk.BOTH, expand=True)
        self.sync_listbox.bind('<<ListboxSelect>>', self.on_sync_select_song)
        
        ttk.Button(frame_list, text="Recargar Lista", command=self.refresh_sync_list).pack(fill=tk.X, pady=5)
        
        # --- Editor Area (Derecha) ---
        frame_editor = ttk.Frame(paned, width=600)
        paned.add(frame_editor, weight=4)
        
        # Info
        self.lbl_sync_title = ttk.Label(frame_editor, text="Editor Visual", font=("Arial", 14, "bold"))
        self.lbl_sync_title.pack(pady=10)
        
        # Selector de formato de tiempo
        format_frame = ttk.Frame(frame_editor)
        format_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(format_frame, text="Formato de tiempo:").pack(side=tk.LEFT, padx=5)
        self.time_format_var = tk.StringVar(value="ms")
        ttk.Radiobutton(format_frame, text="Milisegundos (ms)", variable=self.time_format_var, 
                       value="ms", command=self.on_time_format_change).pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(format_frame, text="Minutos:Segundos (mm:ss)", variable=self.time_format_var, 
                       value="mmss", command=self.on_time_format_change).pack(side=tk.LEFT, padx=10)
        
        # Tabla (Treeview)
        cols = ("#", "Inicio", "Fin", "Texto")
        self.tree = ttk.Treeview(frame_editor, columns=cols, show='headings', height=15)
        
        self.tree.heading("#", text="#")
        self.tree.heading("Inicio", text="Inicio (ms)")
        self.tree.heading("Fin", text="Fin (ms)")
        self.tree.heading("Texto", text="Texto")
        
        self.tree.column("#", width=40, anchor="center")
        self.tree.column("Inicio", width=100, anchor="center")
        self.tree.column("Fin", width=100, anchor="center")
        self.tree.column("Texto", width=400, anchor="w")
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_editor, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        
        # Bind click para editar
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)
        
        # Panel Edición Manual (Bottom)
        edit_frame = ttk.LabelFrame(frame_editor, text="Edición", padding=10)
        edit_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(edit_frame, text="Inicio:").pack(side=tk.LEFT)
        self.entry_time = ttk.Entry(edit_frame, width=12)
        self.entry_time.pack(side=tk.LEFT, padx=5)

        ttk.Label(edit_frame, text="Fin:").pack(side=tk.LEFT, padx=(10,0))
        self.entry_end_time = ttk.Entry(edit_frame, width=12)
        self.entry_end_time.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(edit_frame, text="Texto:").pack(side=tk.LEFT, padx=(15, 0))
        self.entry_text = ttk.Entry(edit_frame, width=40)
        self.entry_text.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(edit_frame, text="Aplicar Cambio", command=self.apply_sync_edit).pack(side=tk.LEFT, padx=15)
        
        # Acciones Globales
        actions_frame = ttk.Frame(frame_editor)
        actions_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(actions_frame, text="💾 GUARDAR CAMBIOS", command=self.save_sync_json).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_frame, text="⏱ Calcular Duración", command=self.calcular_duracion).pack(side=tk.RIGHT, padx=5)
        ttk.Button(actions_frame, text="🗑 Eliminar Línea", command=self.delete_sync_line).pack(side=tk.LEFT, padx=5)
        ttk.Button(actions_frame, text="➕ Añadir Línea", command=self.add_sync_line).pack(side=tk.LEFT, padx=5)

    # --- Lógica Sync Tab ---
    
    def ms_to_mmss(self, ms: int) -> str:
        """Convierte milisegundos a formato mm:ss (redondeando a segundos)"""
        if ms <= 0:
            return ""
        total_seconds = round(ms / 1000)  # Redondear a segundos enteros
        minutes = int(total_seconds // 60)
        seconds = int(total_seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def mmss_to_ms(self, time_str: str) -> int:
        """Convierte formato mm:ss.xxx a milisegundos. También acepta solo segundos o ms directos."""
        time_str = time_str.strip()
        if not time_str:
            return 0
        
        try:
            # Si contiene ':', es formato mm:ss
            if ':' in time_str:
                parts = time_str.split(':')
                minutes = int(parts[0])
                seconds = float(parts[1])
                return int((minutes * 60 + seconds) * 1000)
            else:
                # Si es solo un número, asumimos que son milisegundos
                return int(float(time_str))
        except ValueError:
            raise ValueError(f"Formato de tiempo inválido: {time_str}")
    
    def format_time_for_display(self, ms: int) -> str:
        """Formatea el tiempo según el formato seleccionado."""
        if self.time_format_var.get() == "mmss":
            return self.ms_to_mmss(ms) if ms > 0 else "00:00"
        else:
            return str(ms) if ms > 0 else ""
    
    def parse_time_from_input(self, time_str: str) -> int:
        """Parsea el tiempo del input según el formato seleccionado."""
        time_str = time_str.strip()
        if not time_str:
            return 0
        
        if self.time_format_var.get() == "mmss":
            return self.mmss_to_ms(time_str)
        else:
            return int(time_str)
    
    def on_time_format_change(self):
        """Actualiza la tabla y cabeceras cuando cambia el formato de tiempo."""
        fmt = self.time_format_var.get()
        
        # Actualizar cabeceras de columnas
        if fmt == "mmss":
            self.tree.heading("Inicio", text="Inicio (mm:ss)")
            self.tree.heading("Fin", text="Fin (mm:ss)")
        else:
            self.tree.heading("Inicio", text="Inicio (ms)")
            self.tree.heading("Fin", text="Fin (ms)")
        
        # Refrescar tabla si hay canción cargada
        if hasattr(self, 'current_sync_song') and self.current_sync_song:
            self.populate_tree(self.current_sync_song)
            
            # Refrescar también los campos de edición si hay elemento seleccionado
            if hasattr(self, 'selected_tree_item') and self.selected_tree_item:
                self.on_select_row(None)
    
    def add_sync_line(self):
        """Añade una nueva línea vacía debajo de la seleccionada."""
        if not hasattr(self, 'current_sync_song') or not self.current_sync_song:
            messagebox.showwarning("Aviso", "Seleccione una canción primero")
            return
        
        # Determinar posición de inserción
        insert_idx = len(self.current_sync_song.lineas)  # Por defecto al final
        
        if hasattr(self, 'selected_tree_item') and self.selected_tree_item:
            try:
                current_values = self.tree.item(self.selected_tree_item, "values")
                idx_1based = int(current_values[0])
                insert_idx = idx_1based  # Insertar después de la seleccionada (0-based sería idx_1based)
            except:
                pass
        
        # Crear nueva línea con valores por defecto
        from karaoke_core import Linea
        nueva_linea = Linea(tiempo=0, texto="Nueva línea", tiempo_fin=0)
        
        # Insertar en la posición
        self.current_sync_song.lineas.insert(insert_idx, nueva_linea)
        
        # Refrescar la tabla
        self.populate_tree(self.current_sync_song)
        
        # Seleccionar la nueva línea
        children = self.tree.get_children()
        if insert_idx < len(children):
            new_item = children[insert_idx]
            self.tree.selection_set(new_item)
            self.tree.see(new_item)
            self.selected_tree_item = new_item
            # Cargar valores en los campos de edición
            self.on_select_row(None)
    
    def delete_sync_line(self):
        """Elimina la línea seleccionada."""
        if not hasattr(self, 'current_sync_song') or not self.current_sync_song:
            messagebox.showwarning("Aviso", "Seleccione una canción primero")
            return
        
        if not hasattr(self, 'selected_tree_item') or not self.selected_tree_item:
            messagebox.showwarning("Aviso", "Seleccione una línea para eliminar")
            return
        
        try:
            current_values = self.tree.item(self.selected_tree_item, "values")
            idx_1based = int(current_values[0])
            idx_0based = idx_1based - 1
            
            if 0 <= idx_0based < len(self.current_sync_song.lineas):
                # Confirmar eliminación
                texto_linea = self.current_sync_song.lineas[idx_0based].texto
                if messagebox.askyesno("Confirmar", f"¿Eliminar la línea {idx_1based}?\n\"{texto_linea}\""):
                    del self.current_sync_song.lineas[idx_0based]
                    self.selected_tree_item = None
                    self.populate_tree(self.current_sync_song)
                    
                    # Limpiar campos de edición
                    self.entry_time.delete(0, tk.END)
                    self.entry_end_time.delete(0, tk.END)
                    self.entry_text.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error al eliminar: {e}")

    def calcular_duracion(self):
        """Calcula la duración de la canción basándose en el tiempo_fin del último verso."""
        if not hasattr(self, 'current_sync_song') or not self.current_sync_song:
            messagebox.showwarning("Aviso", "Seleccione una canción primero")
            return
        
        if not self.current_sync_song.lineas:
            messagebox.showwarning("Aviso", "La canción no tiene líneas")
            return
        
        # Buscar el mayor tiempo_fin entre todas las líneas
        max_tiempo_fin = 0
        for linea in self.current_sync_song.lineas:
            if linea.tiempo_fin > max_tiempo_fin:
                max_tiempo_fin = linea.tiempo_fin
        
        if max_tiempo_fin > 0:
            old_duracion = self.current_sync_song.duracion
            self.current_sync_song.duracion = max_tiempo_fin
            
            # Formatear para mostrar al usuario
            segundos = max_tiempo_fin // 1000
            mins = segundos // 60
            secs = segundos % 60
            
            messagebox.showinfo("Duración Calculada", 
                f"Duración actualizada:\n"
                f"  Anterior: {old_duracion} ms\n"
                f"  Nueva: {max_tiempo_fin} ms ({mins:02d}:{secs:02d})\n\n"
                f"Recuerda guardar los cambios.")
        else:
            messagebox.showwarning("Aviso", 
                "No se encontró ningún tiempo_fin > 0 en las líneas.\n"
                "Edita las líneas para establecer los tiempos de fin.")

    def on_sync_select_song(self, event):
        selection = self.sync_listbox.curselection()
        if not selection:
            return
        
        # Obtener canción seleccionada
        cancion = self.gestor.canciones[selection[0]]
        self.current_sync_song = cancion
        
        self.lbl_sync_title.config(text=f"Editando: {cancion.titulo}")
        self.populate_tree(cancion)
        
    def populate_tree(self, cancion):
        # Limpiar
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for i, linea in enumerate(cancion.lineas):
            inicio_fmt = self.format_time_for_display(linea.tiempo) if linea.tiempo > 0 else "0" if self.time_format_var.get() == "ms" else "00:00"
            fin_fmt = self.format_time_for_display(linea.tiempo_fin)
            self.tree.insert("", tk.END, values=(i+1, inicio_fmt, fin_fmt, linea.texto))
            
    def on_select_row(self, event):
        item = self.tree.selection()
        if not item:
            return
        
        values = self.tree.item(item[0], "values")
        # values: #, Inicio, Fin, Texto
        
        self.entry_time.delete(0, tk.END)
        self.entry_time.insert(0, values[1])

        self.entry_end_time.delete(0, tk.END)
        self.entry_end_time.insert(0, values[2])
        
        self.entry_text.delete(0, tk.END)
        self.entry_text.insert(0, values[3])
        
        self.selected_tree_item = item[0]

    def apply_sync_edit(self):
        if not hasattr(self, 'selected_tree_item') or not self.selected_tree_item:
            return
        
        try:
            # Usar las funciones de conversión según el formato seleccionado
            new_time = self.parse_time_from_input(self.entry_time.get())
            new_text = self.entry_text.get()
            
            end_val = self.entry_end_time.get().strip()
            new_end_time = self.parse_time_from_input(end_val) if end_val else 0

            # Obtener datos actuales para indice
            current_values = self.tree.item(self.selected_tree_item, "values")
            idx_1based = int(current_values[0])
            idx_0based = idx_1based - 1

            # Actualizar objeto memoria
            if self.current_sync_song and 0 <= idx_0based < len(self.current_sync_song.lineas):
                current_line = self.current_sync_song.lineas[idx_0based]
                
                # Detectar si cambiamos el TIEMPO DE FIN
                old_end_time = current_line.tiempo_fin
                
                # Actualizar línea actual
                current_line.tiempo = new_time
                current_line.texto = new_text
                current_line.tiempo_fin = new_end_time
                
                # LÓGICA DE ENCADENADO:
                # Si el usuario ha puesto un tiempo de fin, y existe una siguiente línea,
                # actualizar el inicio de la siguiente línea para que coincida.
                
                if new_end_time > 0 and idx_0based < len(self.current_sync_song.lineas) - 1:
                    next_line = self.current_sync_song.lineas[idx_0based + 1]
                    # Solo actualizamos el inicio del siguiente si ha cambiado nuestro fin
                    if new_end_time != old_end_time:
                         next_line.tiempo = new_end_time
                
                # AUTO-CALCULAR DURACIÓN: Si es la última línea y la duración es 0
                if idx_0based == len(self.current_sync_song.lineas) - 1:
                    if new_end_time > 0 and self.current_sync_song.duracion == 0:
                        self.current_sync_song.duracion = new_end_time
            
            # Refrescar toda la tabla para ver cambios
            self.populate_tree(self.current_sync_song)
                
        except ValueError as e:
            if self.time_format_var.get() == "mmss":
                messagebox.showerror("Error", f"Formato de tiempo inválido. Use mm:ss (ej: 01:30)\n{e}")
            else:
                messagebox.showerror("Error", "Los tiempos deben ser números enteros (milisegundos)")

    def save_sync_json(self):
        if not hasattr(self, 'current_sync_song') or not self.current_sync_song:
            return
            
        data = {
            "id": self.current_sync_song.id,
            "titulo": self.current_sync_song.titulo,
            "artista": self.current_sync_song.artista,
            "duracion": self.current_sync_song.duracion,
            "lineas": []
        }
        
        for l in self.current_sync_song.lineas:
            line_dict = {
                "tiempo": l.tiempo,
                "texto": l.texto
            }
            if l.tiempo_fin > 0:
                line_dict["tiempo_fin"] = l.tiempo_fin
            data["lineas"].append(line_dict)
        
        filepath = ""
        if hasattr(self.current_sync_song, 'filepath') and self.current_sync_song.filepath:
            filepath = self.current_sync_song.filepath
        else:
            safe_title = "".join([c for c in self.current_sync_song.titulo if c.isalnum() or c in (' ','-','_')]).strip().lower()
            filepath = f"canciones/{safe_title}.json"

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Guardado", f"Cambios guardados en:\n{filepath}")
            
            # Guardar referencia para restaurar selección
            saved_path = filepath
            
            # Recargar todo (lee de disco)
            self.refresh_song_list() 
            
            # Intentar restaurar selección en la lista de sync
            # Buscamos índice de la canción que coincida con el path guardado
            idx_found = -1
            for i, c in enumerate(self.gestor.canciones):
                # Comparamos paths normalizados o strings simples
                if str(c.filepath) == str(saved_path):
                    idx_found = i
                    self.current_sync_song = c # Actualizar referencia a la nueva instancia
                    break
            
            if idx_found >= 0:
                self.sync_listbox.selection_clear(0, tk.END)
                self.sync_listbox.selection_set(idx_found)
                self.sync_listbox.see(idx_found) # Scroll si es necesario
                # Refrescar árbol con la nueva instancia cargada del disco (confirmación visual)
                self.populate_tree(self.current_sync_song)
            
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))


    # --- Lógica de UI ---

    def refresh_song_list(self):
        """Recarga todas las canciones del disco y actualiza ambas listas (reproductor y sincronizador)."""
        self.gestor.cargar_canciones()
        self._update_player_listbox()
        self._update_sync_listbox()
            
    def filter_songs(self, *args):
        """Filtra la lista del reproductor según el texto de búsqueda.
        Nota: NO recarga del disco ni afecta a la lista de sincronización."""
        query = self.search_var.get()
        canciones = self.gestor.buscar(query)
        self.listbox.delete(0, tk.END)
        for c in canciones:
            self.listbox.insert(tk.END, f"{c.titulo} - {c.artista}")
            
    def _update_player_listbox(self):
        """Actualiza la listbox del reproductor con todas las canciones (respetando filtro)."""
        self.filter_songs()
    
    def _update_sync_listbox(self):
        """Actualiza la listbox de sincronización con las canciones del gestor."""
        if hasattr(self, 'sync_listbox'):
            self.sync_listbox.delete(0, tk.END)
            for c in self.gestor.canciones:
                self.sync_listbox.insert(tk.END, f"{c.titulo} - {c.artista}")
    
    def refresh_sync_list(self):
        """Recarga las canciones del disco y actualiza la lista de sincronización."""
        self.gestor.cargar_canciones()
        self._update_sync_listbox()
    
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

    def send_hide_event(self):
        """Wrapper para llamar a send_hide desde thread safe y resetear estado."""
        def _clear():
            self.lbl_live_text.config(text="...")
            self.send_hide()
            # IMPORTANTE: Si hubo pausa musical, la siguiente frase debe entrar como 'Entra', no 'Cambio'.
            self.first_line_done = False 
            
        self.root.after(0, _clear)

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
