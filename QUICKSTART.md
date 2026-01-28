# 🎤 QUICKSTART - Guía de Inicio Rápido

## ¿Qué hace este proyecto?

Convierte un archivo de texto con letras de canciones en una base de datos JSON estructurada y lista para:
- 🔍 Buscar canciones por título o artista
- 📝 Ver letras formateadas
- ⏱️ Sincronizar tiempos con música
- 🎨 Integrar en apps gráficas de karaoke

## Instalación (1 minuto)

```bash
# No requiere instalación, solo Python 3.6+
cd c:\Users\Mario\Desktop\Proyectos_NET\KaraokeScript
```

## Primeros pasos (5 minutos)

### 1. Ver todas las canciones
```bash
python karaoke.py list
```
✅ Resultado: Listado de 19 canciones con número de líneas

### 2. Ver letra de una canción
```bash
python karaoke.py show "bandido"
```
✅ Resultado: Letra completa formateada

### 3. Buscar canciones
```bash
python karaoke.py search "alaska"
```
✅ Resultado: Todas las canciones de Alaska

### 4. Obtener datos en JSON
```bash
python karaoke.py export "bandido"
```
✅ Resultado: JSON puro con estructura lista para UI

## Próximo Paso: Sincronización ⚡

Una vez tengas un archivo MP3 de una canción:

```bash
# Editar tiempos de forma interactiva
python sync_editor.py canciones/bandido.json
```

Opciones en el editor:
1. Ver letra actual con tiempos
2. Sincronizar línea por línea escuchando
3. Ajustar tiempo de una línea específica
4. Generar tiempos automáticos (estimado)
5. Cargar tiempos desde archivo
6. Guardar cambios

## Estructura de un JSON de Canción

```json
{
  "id": 1,
  "titulo": "BANDIDO",
  "artista": "AZUCAR MORENO",
  "duracion": 0,
  "lineas": [
    {"tiempo": 0, "texto": "La luna me embrujó..."},
    {"tiempo": 0, "texto": "veneno del amor..."}
  ]
}
```

**Campos:**
- `id`: Identificador único
- `titulo`: Nombre de la canción
- `artista`: Cantante/grupo
- `duracion`: Duración en milisegundos
- `lineas`: Array de líneas con:
  - `tiempo`: En ms desde el inicio (para sincronización)
  - `texto`: Contenido de la línea

## Comandos Disponibles

```bash
# Listar todas las canciones
python karaoke.py list

# Ver letra de una canción
python karaoke.py show "<nombre>"

# Buscar por título o artista
python karaoke.py search "<termino>"

# Ver información detallada (con tiempos)
python karaoke.py info "<nombre>"

# Exportar JSON puro
python karaoke.py export "<nombre>"

# Editor de sincronización
python sync_editor.py "<ruta_json>"

# Regenerar JSONs desde texto
python parser_karaoke.py
```

## Ejemplos Prácticos

```bash
# Ver las canciones de un artista
python karaoke.py search "sergio dalma"

# Obtener JSON para usar en tu app
python karaoke.py export "obsesión" > obsesion.json

# Sincronizar una canción
python sync_editor.py canciones/cuando_tú_vas.json

# Ver todas las canciones disponibles
python karaoke.py list
```

## Archivos Importantes

| Archivo | Propósito |
|---------|-----------|
| `karaoke.py` | ⭐ Aplicación principal - usar esto |
| `parser_karaoke.py` | Convierte .txt a JSON |
| `sync_editor.py` | Sincronizar tiempos |
| `canciones/` | Carpeta con 19 JSONs |
| `Karaoke.txt` | Archivo original de texto |

## Próximos Pasos

1. **Sincronización Manual** (Hoy)
   - Obtén MP3s de las canciones
   - Usa `sync_editor.py` para sincronizar
   - Ver: `PROXIMOS_PASOS.md`

2. **Interfaz Gráfica** (Próximo)
   - Ver ejemplos en: `EJEMPLOS_INTEGRACION.md`
   - Pygame, PyQt, o Web

3. **Reproducción en Tiempo Real** (Avanzado)
   - Mostrar letra sincronizada con música
   - Controles de reproducción

## Archivos Incluidos

- `README.md` - Documentación completa
- `PROYECTO_RESUMEN.md` - Resumen ejecutivo
- `PROXIMOS_PASOS.md` - Guía de fases futuras
- `EJEMPLOS_INTEGRACION.md` - Ejemplos de código
- `EJEMPLO_BANDIDO_SINCRONIZADO.json` - JSON con tiempos ejemplo
- `QUICKSTART.md` - Este archivo

## Solución Rápida de Problemas

**P: ¿Cómo agrego más canciones?**
- Edita `Karaoke.txt` con el formato: `"TITULO" ARTISTA\nletra...`
- Ejecuta: `python parser_karaoke.py`

**P: ¿Cómo sincronizo una canción?**
- Ejecuta: `python sync_editor.py canciones/nombre.json`
- Opción 2 para sincronizar escuchando

**P: ¿Cómo uso los JSONs en mi app?**
- Ver ejemplos en `EJEMPLOS_INTEGRACION.md`

**P: ¿Puedo cambiar la estructura del JSON?**
- Sí, pero asegúrate de actualizar `karaoke.py`
- Mejor: mantén la estructura y agrega campos

**P: Los caracteres acentuados se ven raro en PowerShell**
- Normal en PowerShell, los JSONs están bien
- Usa: `python karaoke.py export "cancion"` en editor de texto

## Próximo: Integración Gráfica

```python
# Ejemplo mínimo para mostrar letra sincronizada

import json
import time

# Cargar canción
with open('canciones/bandido.json', 'r') as f:
    cancion = json.load(f)

# Obtener línea en tiempo 15 segundos
tiempo_ms = 15000
for linea in cancion['lineas']:
    if linea['tiempo'] <= tiempo_ms:
        print(f"✓ Mostrando: {linea['texto']}")
```

---

## ¿Tienes dudas?

1. Lee `README.md` para documentación completa
2. Mira `EJEMPLOS_INTEGRACION.md` para código de ejemplo
3. Consulta `PROXIMOS_PASOS.md` para las siguientes fases

**¡Listo para comenzar!** 🚀
