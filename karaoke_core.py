import json
import os
import time
import threading
from pathlib import Path
from typing import List, Dict, Optional, Callable

class Linea:
    def __init__(self, tiempo: int, texto: str, tiempo_fin: int = 0):
        self.tiempo = tiempo # milisegundos inicio
        self.texto = texto
        self.tiempo_fin = tiempo_fin # milisegundos fin (0 = hasta siguiente)

class Cancion:
    def __init__(self, id_cancion, titulo, artista, duracion, lineas: List[Linea], filepath: str = ""):
        self.id = id_cancion
        self.titulo = titulo
        self.artista = artista
        self.duracion = duracion # milisegundos
        self.lineas = lineas
        self.filepath = filepath
    
    @classmethod
    def from_dict(cls, data: Dict, filepath: str = ""):
        # Leemos tiempo_fin si existe, si no 0
        lineas = [Linea(l['tiempo'], l['texto'], l.get('tiempo_fin', 0)) for l in data.get('lineas', [])]
        # Ordenar líneas por tiempo por seguridad
        lineas.sort(key=lambda x: x.tiempo)
        return cls(
            id_cancion=data.get('id', 0),
            titulo=data.get('titulo', 'Desconocido'),
            artista=data.get('artista', 'Desconocido'),
            duracion=data.get('duracion', 0),
            lineas=lineas,
            filepath=filepath
        )

    def get_duration_formatted(self):
        seconds = self.duracion // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

class GestorKaraoke:
    def __init__(self, carpeta_canciones: str = "canciones"):
        self.carpeta_canciones = carpeta_canciones
        self.canciones = [] # Lista de objetos Cancion
        self.cargar_canciones()
    
    def cargar_canciones(self) -> None:
        self.canciones = []
        if not os.path.exists(self.carpeta_canciones):
            return
        
        for archivo in sorted(Path(self.carpeta_canciones).glob("*.json")):
            try:
                with open(archivo, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    # Convertir path a string absoluto o relativo consistente
                    fpath = str(archivo)
                    cancion = Cancion.from_dict(datos, filepath=fpath)
                    self.canciones.append(cancion)
            except Exception as e:
                print(f"Error cargando {archivo}: {e}")

    def buscar(self, query: str) -> List[Cancion]:
        if not query:
            return self.canciones
        q = query.lower()
        return [c for c in self.canciones if q in c.titulo.lower() or q in c.artista.lower()]

class KaraokeEngine:
    """
    Controlador de la reproducción.
    Maneja el temporizador y dispara eventos.
    """
    def __init__(self):
        self.cancion_actual: Optional[Cancion] = None
        self.playing = False
        self.start_time = 0
        self.pause_time = 0 
        self.elapsed_offset = 0 # Tiempo acumulado antes de pausa
        
        # Callbacks
        self.on_progress: Optional[Callable[[int, int], None]] = None # (current_ms, total_ms)
        self.on_lyric: Optional[Callable[[str], None]] = None # (texto)
        self.on_clear: Optional[Callable[[], None]] = None # Aviso para limpiar/ocultar texto
        self.on_finish: Optional[Callable[[], None]] = None
        
        self._stop_flag = False
        self._thread = None
        
        # Estado interno
        self.next_line_idx = 0
        self.current_playing_line: Optional[Linea] = None

    def load_song(self, cancion: Cancion):
        self.stop()
        self.cancion_actual = cancion
        self.next_line_idx = 0
        self.elapsed_offset = 0
        self.current_playing_line = None

    def play(self):
        if not self.cancion_actual:
            return
        
        if self.playing:
            return

        self.playing = True
        self._stop_flag = False
        self.start_time = time.time() * 1000 # ms
        
        self._thread = threading.Thread(target=self._loop)
        self._thread.daemon = True
        self._thread.start()

    def pause(self):
        if not self.playing:
            return
        self.playing = False
        self._stop_flag = True
        # Guardar offset
        now = time.time() * 1000
        self.elapsed_offset += (now - self.start_time)

    def stop(self):
        self.playing = False
        self._stop_flag = True
        self.elapsed_offset = 0
        self.next_line_idx = 0
        self.current_playing_line = None
        if self.on_progress:
            self.on_progress(0, self.cancion_actual.duracion if self.cancion_actual else 0)

    def _loop(self):
        while not self._stop_flag and self.playing:
            now = time.time() * 1000
            current_time = (now - self.start_time) + self.elapsed_offset
            
            # 1. Notificar progreso
            if self.on_progress and self.cancion_actual:
                self.on_progress(int(current_time), self.cancion_actual.duracion)
            
            # 2. Comprobar inicio de líneas
            if self.cancion_actual and self.next_line_idx < len(self.cancion_actual.lineas):
                next_line = self.cancion_actual.lineas[self.next_line_idx]
                if current_time >= next_line.tiempo:
                    # Toca enviar línea
                    self.current_playing_line = next_line
                    if self.on_lyric:
                        self.on_lyric(next_line.texto)
                    self.next_line_idx += 1
            
            # 3. Comprobar fin de línea (silencio)
            # Solo si la línea actual tiene definido un tiempo de fin > 0
            if self.current_playing_line and self.current_playing_line.tiempo_fin > 0:
                # Comprobamos si ya pasó su tiempo de fin
                if current_time >= self.current_playing_line.tiempo_fin:
                    # Verificar que NO hayamos entrado ya en la siguiente línea
                    # (Si la siguiente línea empieza justo en el mismo ms, la lógica de arriba ya la habrá lanzado,
                    # así que 'current_playing_line' ya sería la nueva. Esto ocurre si next_line.tiempo <= tiempo_fin.
                    # Pero si hay gap, current_time >= fin y todavía no llegamos a next_line.tiempo)
                    
                    # Simplemente disparar clear. Si entra la nueva, on_lyric sobreescribirá.
                    # Para evitar parpadeo si coinciden exactamente, podríamos chequear algo más, 
                    # pero comúnmente on_lyric gana.
                    
                    # Debemos evitar disparar clear repetidamente.
                    # Una forma es quitar current_playing_line después de limpiar.
                    if self.on_clear:
                        self.on_clear()
                    self.current_playing_line = None

            # 4. Fin de canción
            if self.cancion_actual and current_time > self.cancion_actual.duracion:
                self.stop()
                if self.on_finish:
                    self.on_finish()
                break
                
            time.sleep(0.05) # 50ms precisión
