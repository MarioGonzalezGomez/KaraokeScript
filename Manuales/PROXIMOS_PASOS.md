# GUÍA DE SINCRONIZACIÓN - Próximos Pasos

## Estado Actual ✅

Ya tienes:
- ✅ 19 canciones parseadas en JSON
- ✅ Sistema CLI completo para gestionar canciones
- ✅ Estructura JSON lista para sincronización
- ✅ Editor interactivo de tiempos

## Próximas Fases

### Fase 1: Sincronización Manual (Ahora)

**Opción A: Editor interactivo integrado**
```bash
python sync_editor.py canciones/bandido.json
```

Este editor permite:
1. Ver letra con tiempos actuales
2. Sincronizar línea por línea escuchando la canción
3. Ajustar tiempos específicos
4. Generar tiempos automáticos (estimado)
5. Cargar tiempos desde archivo
6. Guardar cambios

**Opción B: Herramientas externas**
- **Audacity** + manualmente anotar tiempos
- **LyricFier** o editores LRC online
- Exportar desde **MusixMatch** (si está disponible)

---

### Fase 2: Análisis Automático de Audio (Intermedio)

Cuando quieras automatizar los tiempos:

```python
# Opción 1: Detección de cambios de voz/ritmo
import librosa

y, sr = librosa.load('cancion.mp3')
# Detectar puntos de ataque (cuando comienza cada línea)
onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
onset_times = librosa.frames_to_time(onset_frames, sr=sr)
```

```python
# Opción 2: Transcripción automática + alineación
from openai import OpenAI
import speech_recognition as sr

# Usar Whisper para transcribir
# Luego alinear con las líneas conocidas
```

---

### Fase 3: Visualización Gráfica (Siguiente)

Una vez tengas los tiempos sincronizados, crea una app para mostrar las letras:

**Opción 1: Pygame (Juegos/Gráficos rápidos)**
```python
import pygame
import json
from mutagen.mp3 import MP3

class KaraokeApp:
    def __init__(self, cancion_json, audio_file):
        self.cancion = self.cargar_cancion(cancion_json)
        self.audio = pygame.mixer.Sound(audio_file)
        self.tiempo_actual = 0
    
    def renderizar_letra(self, tiempo_ms):
        # Mostrar solo las líneas cuyo tiempo <= tiempo_actual
        for linea in self.cancion['lineas']:
            if linea['tiempo'] <= tiempo_ms:
                # Resaltar esta línea
                self.mostrar_linea_resaltada(linea)
```

**Opción 2: PyQt/Tkinter (Interfaz más profesional)**
```python
import tkinter as tk
from tkinter import ttk

class VentanaKaraoke:
    def __init__(self):
        self.ventana = tk.Tk()
        self.label_linea_actual = tk.Label(font=("Arial", 24))
        self.label_linea_siguiente = tk.Label(font=("Arial", 14), fg="gray")
```

**Opción 3: Electron/JavaScript (Web-based)**
- Crear versión web con HowlerJS para audio
- Mostrar líneas sincronizadas en HTML5
- Estilizar como un reproductor Spotify

---

### Fase 4: Integración de Reproducción (Avanzado)

```python
import pygame
from dataclasses import dataclass
from typing import List

@dataclass
class LineaKaraoke:
    tiempo: int  # ms
    texto: str
    duracion: int = 0  # ms hasta la siguiente línea

class ReproductorKaraoke:
    def __init__(self, cancion_json: str, archivo_audio: str):
        self.cancion = self.cargar(cancion_json)
        self.tiempo_inicio = None
        self.en_pausa = False
    
    def obtener_linea_actual(self) -> LineaKaraoke:
        """Retorna la línea que debe mostrarse ahora"""
        tiempo_transcurrido = pygame.mixer.music.get_busy()
        for linea in self.cancion['lineas']:
            if linea['tiempo'] <= tiempo_transcurrido < linea['tiempo'] + 2000:
                return linea
```

---

## Archivos a Crear en Orden

```
Fase 1 (ACTUAL):
└── Usar: sync_editor.py (ya existe)

Fase 2:
└── audio_analyzer.py
    ├── Detectar onset points
    ├── Sincronización automática
    └── Exportar tiempos

Fase 3:
├── ui/
│   ├── karaoke_pygame.py
│   ├── karaoke_tkinter.py
│   └── assets/
│       ├── estilos.css
│       └── fonts/
└── reproductor_grafico.py

Fase 4:
├── reproductor_avanzado.py
├── gestos_multitáctil.py
└── estadísticas.py
```

---

## Recomendación Inmediata

**Comienza con la Fase 1:**

1. Elige **una canción de prueba** (ej: "BANDIDO")
2. Obtén el **archivo de audio** (MP3/WAV)
3. Usa `python sync_editor.py canciones/bandido.json`
4. Selecciona opción **5** (generar tiempos automáticos como base)
5. Luego opción **2** (ajusta manualmente escuchando)
6. Guarda con opción **6**

Esto te dará una canción completamente sincronizada para la Fase 3.

---

## Recursos Útiles

### APIs de Sincronización (Podrían ayudar):
- **MusixMatch API**: `pip install musixmatch`
- **Genius API**: Letras pero sin tiempos
- **YouTube Music**: A veces tiene tiempos en comentarios

### Librerías Python Recomendadas:
```bash
# Para análisis de audio
pip install librosa soundfile pydub

# Para reproducción
pip install pygame mutagen

# Para UI gráfica
pip install pygame PyQt6 tkinter

# Para transcripción automática
pip install openai-whisper speech_recognition

# Para procesamiento de video/frames
pip install opencv-python
```

### Herrramietas Externas:
- **Audacity**: Marcar tiempos manualmente (libre)
- **LyricFier**: Editor LRC online
- **UltraStar Creator**: Crear karaokes profesionales
- **ffmpeg**: Procesar audio/video

---

## Próximo Paso Recomendado

```bash
# 1. Consigue un archivo de audio de una canción
# 2. Ejecuta el editor de sincronización
python sync_editor.py canciones/bandido.json

# 3. Genera tiempos automáticos (opción 5)
# 4. Ajusta manualmente escuchando (opción 2)
# 5. Guarda (opción 6)

# 6. Verifica el resultado
python karaoke.py info "bandido"
```

¿Quieres que continúe con la Fase 2 o Fase 3 directamente?
