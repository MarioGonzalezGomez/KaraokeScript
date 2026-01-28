# 🎤 Sistema de Karaoke - Documentación

## Descripción

Sistema completo para parsear, gestionar y mostrar letras de canciones en formato JSON para aplicaciones de karaoke.

## Estructura del Proyecto

```
KaraokeScript/
├── Karaoke.txt              # Archivo original con todas las canciones
├── parser_karaoke.py        # Script para parsear Karaoke.txt y generar JSONs
├── karaoke.py               # Aplicación principal con CLI
└── canciones/               # Carpeta con JSONs de cada canción
    ├── bandido.json
    ├── 20_de_enero.json
    ├── sobreviviré.json
    └── ... (19 canciones total)
```

## Instalación

No requiere dependencias externas. Solo necesitas Python 3.6+

```bash
# Asegúrate de estar en el directorio del proyecto
cd KaraokeScript
```

## Uso

### 1. Generar JSONs desde Karaoke.txt

Si necesitas regenerar los JSONs desde el archivo de texto:

```bash
python parser_karaoke.py
```

Esto:
- Parsea el archivo `Karaoke.txt`
- Extrae título, artista y letra de cada canción
- Crea un JSON para cada canción en la carpeta `canciones/`
- Imprime un resumen del proceso

### 2. Listar todas las canciones

```bash
python karaoke.py list
```

**Salida:**
```
======================================================================
📋 CANCIONES DISPONIBLES (19 total)
======================================================================

 1. 20 DE ENERO                              | LA OREJA DE VAN GOGH           (36 líneas)
 2. A QUIEN LE IMPORTA                       | ALASKA                         (41 líneas)
 3. BAILAR PEGADOS                           | DE SERGIO DALMA                (52 líneas)
 ...
```

### 3. Ver la letra de una canción

```bash
python karaoke.py show "bandido"
```

O con el título completo:
```bash
python karaoke.py show "BANDIDO"
```

También funciona con búsqueda parcial:
```bash
python karaoke.py show "enero"
```

### 4. Buscar canciones

```bash
python karaoke.py search "alaska"
python karaoke.py search "amor"
```

Busca en títulos y artistas.

### 5. Información detallada

```bash
python karaoke.py info "y yo te besé"
```

Muestra:
- Título y artista
- Número de líneas
- Duración (cuando esté configurada)
- Todas las líneas con sus tiempos (actualmente todos en 0 ms)

### 6. Exportar como JSON

```bash
python karaoke.py export "bandido" > mi_cancion.json
```

Exporta los datos de una canción en formato JSON puro.

## Formato JSON de una Canción

Cada canción se guarda como JSON con esta estructura:

```json
{
  "id": 1,
  "titulo": "BANDIDO",
  "artista": "AZUCAR MORENO",
  "duracion": 0,
  "lineas": [
    {
      "tiempo": 0,
      "texto": "La luna me embrujó y me llevó hasta ti,"
    },
    {
      "tiempo": 0,
      "texto": "veneno del amor que yo feliz bebí"
    }
  ]
}
```

### Campos:
- **id**: Número identificador único (1-19)
- **titulo**: Nombre de la canción
- **artista**: Nombre del artista/grupo
- **duracion**: Duración total en milisegundos (por ahora 0)
- **lineas**: Array de líneas de la letra
  - **tiempo**: Timestamp en milisegundos cuando aparece esta línea
  - **texto**: Contenido de la línea

## Próximos Pasos

### Sincronización de Tiempos

Para la próxima fase, necesitamos agregar tiempos precisos a cada línea. Las opciones son:

1. **Manual**: Usar una herramienta de edición (Audacity) mientras escuchas
2. **Semi-automático**: Procesar audio con librosa/Whisper
3. **APIs externas**: MusixMatch, KaraFun (requiere acceso)

### Integración Gráfica

Una vez con los tiempos, podemos:
- Crear una interfaz gráfica en Python (Tkinter, PyQt, Pygame)
- Mostrar las líneas sincronizadas con la música
- Resaltar la línea actual en tiempo real
- Controles de reproducción (play, pause, seek)

## Ejemplos de Comandos Prácticos

```bash
# Ver todas las canciones
python karaoke.py list

# Mostrar canción específica
python karaoke.py show "bandido"

# Buscar todas las de un artista
python karaoke.py search "alaska"

# Ver estructura JSON completa de una canción
python karaoke.py export "como una ola"

# Guardar JSON en archivo
python karaoke.py export "cuando tú vas" > cuando_tu_vas.json

# Ver información con tiempos (cuando estén agregados)
python karaoke.py info "obsesión"
```

## Notas Importantes

- Los nombres de canciones son **insensibles a mayúsculas** (case-insensitive)
- Las búsquedas también funcionan por búsqueda parcial en titulo y artista
- Actualmente todos los tiempos están en 0 ms (se configurarán en la siguiente fase)
- Los JSONs están en UTF-8 para soportar caracteres acentuados
- El parser es robusto y maneja líneas vacías automáticamente

## Solución de Problemas

### Error: "No se encontró 'Karaoke.txt'"
- Asegúrate de estar en el directorio correcto
- El archivo debe estar en la misma carpeta que los scripts Python

### Error: "Carpeta 'canciones' no encontrada"
- Ejecuta primero: `python parser_karaoke.py`
- Esto creará la carpeta y los JSONs

### Los caracteres acentuados se ven mal en PowerShell
- Es un problema de PowerShell, no de los datos
- Los JSONs están correctamente guardados en UTF-8
- Verifica con: `python karaoke.py export "bandido"` y abre en editor de texto

## Autor

Creado como base para un sistema de karaoke con sincronización gráfica.
