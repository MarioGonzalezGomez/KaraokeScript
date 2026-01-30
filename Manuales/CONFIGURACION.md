# ⚙️ CONFIGURACIÓN Y PERSONALIZACIÓN

## Variables de Configuración Útiles

Puedes crear un archivo `config.json` en la raíz del proyecto:

```json
{
  "carpeta_canciones": "canciones",
  "carpeta_audio": "audio",
  "idioma": "es",
  "tema": "dark",
  "fps": 30,
  "encoding": "utf-8",
  "busqueda": {
    "case_sensitive": false,
    "busqueda_parcial": true,
    "buscar_en_artista": true
  },
  "sincronizacion": {
    "tiempo_minimo_por_linea": 500,
    "tiempo_maximo_por_linea": 5000
  },
  "reproduccion": {
    "volumen": 0.8,
    "velocidad": 1.0,
    "modo_practica": false
  }
}
```

## Mejoras Sugeridas para Futuros Desarrollos

### 1. Agregación de Metadatos
```json
{
  "id": 1,
  "titulo": "BANDIDO",
  "artista": "AZUCAR MORENO",
  "año": 1983,
  "genero": "Rumba Española",
  "dificultad": "media",
  "rango_notas": "E3-C5",
  "idioma": "es",
  "tags": ["romance", "pasión", "clásico"],
  "sincroni": false,
  "duracion": 0,
  "lineas": []
}
```

### 2. Sistema de Versiones de Sincronización
```json
{
  "sincronizaciones": [
    {
      "version": 1,
      "fecha": "2024-01-28",
      "editor": "usuario",
      "lineas": [...]
    },
    {
      "version": 2,
      "fecha": "2024-01-29",
      "editor": "usuario",
      "lineas": [...]
    }
  ]
}
```

### 3. Soporte para Múltiples Idiomas
```
canciones/
├── es/     # Español
├── en/     # Inglés
├── fr/     # Francés
└── pt/     # Portugués
```

### 4. Base de Datos SQL Alternativa
```sql
CREATE TABLE canciones (
    id INTEGER PRIMARY KEY,
    titulo TEXT NOT NULL,
    artista TEXT NOT NULL,
    genero TEXT,
    duracion INTEGER,
    fecha_agregada TIMESTAMP,
    sincronizada BOOLEAN
);

CREATE TABLE lineas (
    id INTEGER PRIMARY KEY,
    cancion_id INTEGER,
    numero_linea INTEGER,
    tiempo INTEGER,
    texto TEXT,
    FOREIGN KEY(cancion_id) REFERENCES canciones(id)
);
```

## Estructura Extendida del Proyecto

```
KaraokeScript/
├── config.json              # Configuración global
├── requirements.txt         # Dependencias Python
├── setup.py                 # Instalador
├── .gitignore              # Git ignore
│
├── 📚 docs/
│   ├── QUICKSTART.md
│   ├── README.md
│   ├── API.md              # Documentación de API
│   └── ARQUITECTURA.md     # Explicación de diseño
│
├── 🐍 src/
│   ├── karaoke.py
│   ├── parser_karaoke.py
│   ├── sync_editor.py
│   ├── models/
│   │   └── cancion.py      # Modelo de datos
│   ├── utils/
│   │   ├── busqueda.py     # Funciones de búsqueda
│   │   └── validacion.py   # Validación de datos
│   └── ui/
│       └── __init__.py     # Para interfaz gráfica
│
├── 🎵 data/
│   ├── canciones/          # JSONs (19)
│   ├── audio/              # MP3s (cuando agregues)
│   └── backups/            # Copias de seguridad
│
├── 🧪 tests/
│   ├── test_parser.py
│   ├── test_karaoke.py
│   └── test_busqueda.py
│
└── 🎨 ui/
    ├── pygame_ui.py        # Interfaz Pygame
    ├── tkinter_ui.py       # Interfaz Tkinter
    └── assets/             # Imágenes, fuentes, etc.
```

## Dependencias Opcionales

```bash
# requirements.txt

# Base
pygame==2.1.3              # Para UI gráfica
PyQt6==6.5.0              # Alternativa UI
mutagen==1.45.1           # Metadatos de audio

# Análisis de audio
librosa==0.10.0           # Procesamiento de audio
soundfile==0.12.1         # Lectura de audio
numpy==1.24.3             # Operaciones numéricas

# Transcripción automática
openai-whisper==20230101  # Transcribir audio
SpeechRecognition==3.10.0 # API de reconocimiento

# Web/API
Flask==2.3.2              # Framework web
FastAPI==0.100.0          # API moderno
uvicorn==0.23.1           # Servidor ASGI

# Base de datos
sqlite3                    # Nativa en Python
sqlalchemy==2.0.19        # ORM

# Testing
pytest==7.4.0             # Framework de testing
pytest-cov==4.1.0         # Coverage

# Herramientas
black==23.7.0             # Formateador de código
pylint==2.17.4            # Linter
mypy==1.4.1               # Type checking
```

## Ejemplo: Modelo de Datos Extendido

```python
# models/cancion.py
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

@dataclass
class Linea:
    numero: int
    tiempo: int  # milisegundos
    texto: str
    tono: Optional[str] = None  # Para karaoke musical
    duracion: Optional[int] = None

@dataclass
class Cancion:
    id: int
    titulo: str
    artista: str
    genero: Optional[str] = None
    año: Optional[int] = None
    idioma: str = "es"
    duracion: int = 0
    sincronizada: bool = False
    fecha_agregada: datetime = None
    lineas: List[Linea] = None
    
    def guardar_json(self, ruta: str):
        """Guarda la canción en JSON"""
        import json
        datos = {
            'id': self.id,
            'titulo': self.titulo,
            'artista': self.artista,
            'genero': self.genero,
            'año': self.año,
            'idioma': self.idioma,
            'duracion': self.duracion,
            'sincronizada': self.sincronizada,
            'lineas': [
                {'numero': l.numero, 'tiempo': l.tiempo, 'texto': l.texto}
                for l in self.lineas
            ]
        }
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
```

## Ejemplo: Búsqueda Avanzada

```python
# utils/busqueda.py
from typing import List, Dict
import re

class BuscadorAvanzado:
    def __init__(self, canciones: List[Dict]):
        self.canciones = canciones
        self.indice = self._crear_indice()
    
    def _crear_indice(self):
        """Crear índice invertido para búsqueda rápida"""
        indice = {}
        for cancion in self.canciones:
            palabras = set()
            palabras.update(cancion['titulo'].lower().split())
            palabras.update(cancion['artista'].lower().split())
            
            for palabra in palabras:
                if palabra not in indice:
                    indice[palabra] = []
                indice[palabra].append(cancion)
        
        return indice
    
    def buscar(self, termino: str, campos=['titulo', 'artista']) -> List[Dict]:
        """Búsqueda rápida usando índice"""
        resultados = set()
        palabras = termino.lower().split()
        
        for palabra in palabras:
            if palabra in self.indice:
                resultados.update(self.indice[palabra])
        
        return list(resultados)
    
    def buscar_regex(self, patron: str) -> List[Dict]:
        """Búsqueda con expresiones regulares"""
        regex = re.compile(patron, re.IGNORECASE)
        return [
            c for c in self.canciones
            if regex.search(c['titulo']) or regex.search(c['artista'])
        ]
    
    def buscar_avanzada(self, **criterios) -> List[Dict]:
        """Búsqueda con múltiples criterios"""
        resultados = self.canciones
        
        if 'artista' in criterios:
            resultados = [
                c for c in resultados 
                if criterios['artista'].lower() in c['artista'].lower()
            ]
        
        if 'genero' in criterios:
            resultados = [
                c for c in resultados 
                if c.get('genero') == criterios['genero']
            ]
        
        if 'año_desde' in criterios:
            resultados = [
                c for c in resultados 
                if c.get('año', 0) >= criterios['año_desde']
            ]
        
        return resultados
```

## Testing

```python
# tests/test_karaoke.py
import pytest
import json
from pathlib import Path

def test_cargar_cancion():
    """Test que carga una canción correctamente"""
    with open('canciones/bandido.json', 'r') as f:
        cancion = json.load(f)
    
    assert cancion['titulo'] == 'BANDIDO'
    assert cancion['artista'] == 'AZUCAR MORENO'
    assert len(cancion['lineas']) > 0

def test_busqueda():
    """Test de búsqueda"""
    from src.utils.busqueda import BuscadorAvanzado
    
    canciones = [
        {'titulo': 'Bandido', 'artista': 'Azúcar Moreno'},
        {'titulo': 'Obsesión', 'artista': 'Aventura'}
    ]
    
    buscador = BuscadorAvanzado(canciones)
    resultados = buscador.buscar('bandido')
    
    assert len(resultados) == 1
    assert resultados[0]['titulo'] == 'Bandido'

def test_validacion():
    """Test de validación de JSON"""
    # Aquí iría validación de esquema
    pass
```

## CI/CD (GitHub Actions)

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: pip install -r requirements.txt
      - run: pytest
      - run: pylint src/
      - run: mypy src/
```

---

## Recomendaciones Finales

1. **Documentación**: Mantén actualizado el README
2. **Testing**: Agrega tests antes de nuevas features
3. **Versionado**: Usa semantic versioning (v1.0.0, v1.1.0, etc.)
4. **Git**: Commit frecuentes y mensajes descriptivos
5. **Código**: Sigue PEP 8, usa type hints
6. **Performance**: Indexa búsquedas para gran volumen
7. **Seguridad**: Valida entrada de usuario
8. **Escalabilidad**: Prepara para agregar más canciones

---

**¡Tu proyecto está listo para crecer!** 🚀
