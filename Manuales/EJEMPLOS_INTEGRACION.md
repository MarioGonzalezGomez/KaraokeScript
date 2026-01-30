# Ejemplos de Integración - KaraokeScript

Este archivo contiene ejemplos de cómo integrar KaraokeScript en tus propias aplicaciones.

## Ejemplo 1: Usar el Gestor de Canciones en tu código

```python
import json
from pathlib import Path

class GestorCancionesIntegrado:
    def __init__(self, carpeta_canciones="canciones"):
        self.carpeta = Path(carpeta_canciones)
        self.cache = {}
    
    def cargar_cancion(self, nombre_cancion):
        """Carga una canción desde JSON"""
        # Buscar archivo JSON
        for archivo in self.carpeta.glob("*.json"):
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                if datos['titulo'].lower() == nombre_cancion.lower():
                    return datos
        return None
    
    def obtener_linea_en_tiempo(self, cancion, tiempo_ms):
        """Retorna la línea que debe mostrarse en ese momento"""
        linea_actual = None
        linea_siguiente = None
        
        for linea in cancion['lineas']:
            if linea['tiempo'] <= tiempo_ms:
                linea_actual = linea
            elif linea['tiempo'] > tiempo_ms and linea_siguiente is None:
                linea_siguiente = linea
        
        return {
            'actual': linea_actual,
            'siguiente': linea_siguiente
        }

# Uso
gestor = GestorCancionesIntegrado()
cancion = gestor.cargar_cancion("bandido")
lineas = gestor.obtener_linea_en_tiempo(cancion, 15000)  # 15 segundos
print(f"Ahora: {lineas['actual']['texto']}")
print(f"Próxima: {lineas['siguiente']['texto']}")
```

---

## Ejemplo 2: Reproductor Básico con Pygame

```python
import pygame
import json
import time
from pathlib import Path

class ReproductorKaraokeBasico:
    def __init__(self, archivo_cancion_json, archivo_audio_mp3):
        pygame.mixer.init()
        
        # Cargar canción
        with open(archivo_cancion_json, 'r', encoding='utf-8') as f:
            self.cancion = json.load(f)
        
        # Cargar audio
        self.audio = pygame.mixer.Sound(archivo_audio_mp3)
        self.tiempo_inicio = None
        self.reproduciendo = False
    
    def reproducir(self):
        """Inicia la reproducción"""
        self.tiempo_inicio = time.time() * 1000  # ms
        self.audio.play()
        self.reproduciendo = True
    
    def obtener_tiempo_actual(self):
        """Retorna el tiempo actual en ms desde el inicio"""
        if self.tiempo_inicio is None:
            return 0
        return (time.time() * 1000) - self.tiempo_inicio
    
    def obtener_linea_actual(self):
        """Retorna la línea que debe mostrarse ahora"""
        tiempo = self.obtener_tiempo_actual()
        
        for linea in self.cancion['lineas']:
            if linea['tiempo'] <= tiempo < linea['tiempo'] + 3000:  # 3 segundos por línea
                return linea
        
        return None

# Uso
reproductor = ReproductorKaraokeBasico(
    'canciones/bandido.json',
    'canciones_audio/bandido.mp3'
)
reproductor.reproducir()

while reproductor.reproduciendo:
    linea = reproductor.obtener_linea_actual()
    if linea:
        print(f"[{reproductor.obtener_tiempo_actual():.0f}ms] {linea['texto']}")
    time.sleep(0.1)
```

---

## Ejemplo 3: Interfaz CLI Personalizada

```python
import subprocess
import json

class CLIKaraokePersonalizado:
    """Envuelve karaoke.py con funciones personalizadas"""
    
    def listar_canciones_por_artista(self, artista):
        """Lista todas las canciones de un artista"""
        resultado = subprocess.run(
            ['python', 'karaoke.py', 'search', artista],
            capture_output=True,
            text=True
        )
        return resultado.stdout
    
    def obtener_cancion_json(self, nombre_cancion):
        """Obtiene una canción en formato JSON"""
        resultado = subprocess.run(
            ['python', 'karaoke.py', 'export', nombre_cancion],
            capture_output=True,
            text=True
        )
        return json.loads(resultado.stdout)
    
    def crear_playlist(self, lista_canciones):
        """Crea una playlist con varias canciones"""
        playlist = {
            'nombre': 'Mi Playlist',
            'canciones': []
        }
        
        for nombre in lista_canciones:
            cancion = self.obtener_cancion_json(nombre)
            if cancion:
                playlist['canciones'].append(cancion)
        
        return playlist

# Uso
cli = CLIKaraokePersonalizado()

# Buscar artista
print(cli.listar_canciones_por_artista("alaska"))

# Obtener canción
bandido = cli.obtener_cancion_json("bandido")
print(f"Total líneas en Bandido: {len(bandido['lineas'])}")

# Crear playlist
playlist = cli.crear_playlist(["bandido", "cuando tú vas", "obsesión"])
print(f"Playlist creada con {len(playlist['canciones'])} canciones")
```

---

## Ejemplo 4: API REST para tu App Gráfica

```python
# archivo: karaoke_api.py
from flask import Flask, jsonify, request
import json
from pathlib import Path

app = Flask(__name__)

@app.route('/api/canciones', methods=['GET'])
def listar_canciones():
    """Lista todas las canciones disponibles"""
    canciones = []
    for archivo in Path('canciones').glob('*.json'):
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            canciones.append({
                'id': datos['id'],
                'titulo': datos['titulo'],
                'artista': datos['artista'],
                'num_lineas': len(datos['lineas'])
            })
    return jsonify(canciones)

@app.route('/api/cancion/<nombre>', methods=['GET'])
def obtener_cancion(nombre):
    """Obtiene una canción específica"""
    for archivo in Path('canciones').glob('*.json'):
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            if datos['titulo'].lower() == nombre.lower():
                return jsonify(datos)
    return jsonify({'error': 'No encontrada'}), 404

@app.route('/api/cancion/<nombre>/linea/<int:tiempo_ms>', methods=['GET'])
def obtener_linea_en_tiempo(nombre, tiempo_ms):
    """Obtiene la línea que se muestra en un tiempo específico"""
    for archivo in Path('canciones').glob('*.json'):
        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)
            if datos['titulo'].lower() == nombre.lower():
                linea_actual = None
                for linea in datos['lineas']:
                    if linea['tiempo'] <= tiempo_ms:
                        linea_actual = linea
                
                return jsonify({
                    'cancion': nombre,
                    'tiempo': tiempo_ms,
                    'linea': linea_actual
                })
    return jsonify({'error': 'No encontrada'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
```

Uso desde cliente:
```bash
# Terminal 1: Iniciar API
python karaoke_api.py

# Terminal 2: Hacer requests
curl http://localhost:5000/api/canciones
curl http://localhost:5000/api/cancion/bandido
curl http://localhost:5000/api/cancion/bandido/linea/15000
```

---

## Ejemplo 5: Visualizador en Tiempo Real (PyGame)

```python
import pygame
import json
import time
from typing import Optional

class VisualizadorKaraoke:
    def __init__(self, ancho=800, alto=600):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption("Karaoke - Visualizador")
        self.reloj = pygame.time.Clock()
        self.fuente_grande = pygame.font.Font(None, 48)
        self.fuente_pequeña = pygame.font.Font(None, 32)
        
        self.cancion = None
        self.tiempo_inicio = None
    
    def cargar_cancion(self, ruta_json):
        """Carga una canción desde JSON"""
        with open(ruta_json, 'r', encoding='utf-8') as f:
            self.cancion = json.load(f)
    
    def obtener_linea_actual(self) -> Optional[dict]:
        """Retorna la línea que debe mostrarse ahora"""
        if self.tiempo_inicio is None:
            return None
        
        tiempo_actual = (time.time() * 1000) - self.tiempo_inicio
        
        for i, linea in enumerate(self.cancion['lineas']):
            if linea['tiempo'] <= tiempo_actual:
                linea_actual = linea
            else:
                return linea_actual if i > 0 else None
        
        return None
    
    def renderizar(self):
        """Dibuja la pantalla con la letra actual"""
        self.pantalla.fill((0, 0, 0))  # Fondo negro
        
        linea_actual = self.obtener_linea_actual()
        
        if linea_actual:
            # Texto principal (grande, blanco)
            texto_principal = self.fuente_grande.render(
                linea_actual['texto'],
                True,
                (255, 255, 255)
            )
            rect_principal = texto_principal.get_rect(center=(400, 300))
            self.pantalla.blit(texto_principal, rect_principal)
            
            # Información
            if self.tiempo_inicio:
                tiempo = (time.time() * 1000) - self.tiempo_inicio
                info = self.fuente_pequeña.render(
                    f"Tiempo: {tiempo/1000:.1f}s / {self.cancion['duracion']/1000:.1f}s",
                    True,
                    (100, 100, 100)
                )
                self.pantalla.blit(info, (10, 10))
        
        pygame.display.flip()
    
    def ejecutar(self):
        """Loop principal"""
        self.tiempo_inicio = time.time() * 1000
        corriendo = True
        
        while corriendo:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    corriendo = False
                elif evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_SPACE:
                        # Pausa/Reanuda
                        pass
            
            self.renderizar()
            self.reloj.tick(30)  # 30 FPS
        
        pygame.quit()

# Uso
viz = VisualizadorKaraoke()
viz.cargar_cancion('canciones/bandido.json')
viz.ejecutar()
```

---

## Ejemplo 6: Exportador a Formato LRC

```python
import json
from pathlib import Path

def convertir_a_lrc(archivo_json, archivo_lrc_salida):
    """Convierte JSON de karaoke a formato LRC"""
    with open(archivo_json, 'r', encoding='utf-8') as f:
        cancion = json.load(f)
    
    lineas_lrc = [
        f"[ar:{cancion['artista']}]",
        f"[ti:{cancion['titulo']}]",
        f"[al:KaraokeScript]",
        ""
    ]
    
    for linea in cancion['lineas']:
        # Convertir ms a formato LRC [MM:SS.XX]
        tiempo_ms = linea['tiempo']
        minutos = int(tiempo_ms // 60000)
        segundos = int((tiempo_ms % 60000) // 1000)
        centesimas = int((tiempo_ms % 1000) // 10)
        
        linea_lrc = f"[{minutos:02d}:{segundos:02d}.{centesimas:02d}]{linea['texto']}"
        lineas_lrc.append(linea_lrc)
    
    # Guardar
    with open(archivo_lrc_salida, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lineas_lrc))
    
    print(f"✓ Archivo LRC creado: {archivo_lrc_salida}")

# Uso
convertir_a_lrc(
    'canciones/bandido.json',
    'bandido.lrc'
)
```

---

## Resumen de Integraciones Posibles

| Tipo | Descripción | Dificultad |
|------|-------------|-----------|
| **CLI** | Línea de comandos | ⭐ Fácil |
| **API REST** | Servidor Flask/FastAPI | ⭐⭐ Medio |
| **Desktop GUI** | PyQt, Tkinter, Pygame | ⭐⭐ Medio |
| **Web App** | JavaScript + HowlerJS | ⭐⭐⭐ Avanzado |
| **Mobile** | React Native, Flutter | ⭐⭐⭐ Avanzado |

---

¿Necesitas ayuda implementando alguna de estas integraciones?
