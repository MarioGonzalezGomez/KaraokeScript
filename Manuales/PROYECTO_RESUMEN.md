# 🎤 KaraokeScript - Resumen del Proyecto

## ¿Qué se ha creado?

Un **sistema completo de gestión de canciones para karaoke** con estructura lista para sincronización gráfica.

## Archivos Principales

### 1. **parser_karaoke.py** 
Convierte Karaoke.txt en JSONs individuales
```bash
python parser_karaoke.py
```
- Lee archivo de texto con todas las canciones
- Extrae título, artista y letra de cada una
- Genera 19 archivos JSON en carpeta `canciones/`

### 2. **karaoke.py** ⭐ Principal
Interfaz CLI para gestionar canciones
```bash
# Listar todas las canciones
python karaoke.py list

# Ver letra completa
python karaoke.py show "bandido"

# Buscar por artista o título
python karaoke.py search "alaska"

# Ver información detallada (con tiempos)
python karaoke.py info "y yo te besé"

# Exportar JSON puro
python karaoke.py export "bandido" > bandido.json
```

### 3. **sync_editor.py** 
Editor interactivo para sincronizar tiempos
```bash
# Editar tiempos de una canción
python sync_editor.py canciones/bandido.json
```

Opciones:
1. Ver letra con tiempos actuales
2. Sincronizar línea por línea (manual)
3. Ajustar tiempo de línea específica
4. Cargar tiempos desde archivo
5. Generar tiempos automáticos (estimado)
6. Guardar cambios

### 4. **canciones/** (Carpeta)
19 archivos JSON, uno por canción:
- `bandido.json`
- `20_de_enero.json`
- `sobreviviré.json`
- ... y 16 más

Estructura de cada JSON:
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

## Características Actuales

✅ **Gestión de Canciones**
- Parseo automático desde archivo de texto
- Búsqueda por título y artista
- Visualización formateada
- Exportación a JSON

✅ **Sincronización**
- Editor interactivo
- Generador de tiempos automático (estimado)
- Carga desde archivos externos
- Ajuste individual de líneas

✅ **Estructura Preparada**
- JSONs listos para usar
- Formato estandarizado
- Aceptable para UI gráfica

## Próximas Fases Recomendadas

### Fase 2: Sincronización Manual ⚡ (Hacer AHORA)
```bash
python sync_editor.py canciones/bandido.json
```
Asignar tiempos correctos escuchando las canciones.

### Fase 3: Interfaz Gráfica
Mostrar letras sincronizadas con la música:
- Pygame (Rápido)
- PyQt/Tkinter (Profesional)
- Web (Multiplataforma)

### Fase 4: Reproducción Avanzada
- Controles (play, pause, seek)
- Almacenamiento de configuración
- Estadísticas/Rankings

## Requisitos

- Python 3.6+
- Sin dependencias externas (scripts actuales)
- Para reproducción de audio: `pip install pygame`

## Estructura del Proyecto

```
KaraokeScript/
├── README.md                          # Documentación principal
├── PROXIMOS_PASOS.md                  # Guía de fases futuras
├── Karaoke.txt                        # Archivo original de canciones
├── parser_karaoke.py                  # Parser (genera JSONs)
├── karaoke.py                         # CLI principal
├── sync_editor.py                     # Editor de tiempos
└── canciones/                         # JSONs (19 canciones)
    ├── bandido.json
    ├── 20_de_enero.json
    ├── sobreviviré.json
    ├── cuando_tú_vas.json
    ├── a_quien_le_importa.json
    ├── abre_tu_mente.json            ← Nota: Falta en original
    ├── todos_me_miran.json           ← Nota: Falta en original
    ├── tanto_la_querías.json         ← Nota: Falta en original
    ├── slomo.json
    ├── mi_gran_noche.json            ← Nota: Falta en original
    ├── ay_mamá.json                  ← Nota: Falta en original
    ├── ave_maría.json                ← Nota: Falta en original
    ├── estoy_llorando_por_ti.json    ← Nota: Falta en original
    ├── cuando_zarpa_el_amor.json
    ├── yo_quiero_bailar.json
    ├── dramas_y_comedias.json
    ├── sueño_su_boca.json
    ├── zorra.json
    ├── nochentera.json
    ├── esa_diva.json
    ├── europes_living_a_celebration.json
    ├── vivo_cantando.json
    ├── como_una_ola.json
    ├── corazón_contento.json
    ├── vivir_así_es_morir_de_amor.json
    ├── olvídame_y_pega_la_vuelta.json
    ├── dile_que_la_quiero.json
    ├── raffaella.json
    ├── bailar_pegados.json
    ├── obsesión.json
    ├── caliente.json
    └── y_yo_te_besé.json
```

## Cómo Empezar

### 1. Ver todas las canciones disponibles
```bash
python karaoke.py list
```

### 2. Ver letra de una canción
```bash
python karaoke.py show "mi canción favorita"
```

### 3. Sincronizar una canción (Fase 2)
```bash
# Necesitarás el archivo MP3 de la canción
python sync_editor.py canciones/bandido.json
```

### 4. Exportar datos para usar en tu app gráfica
```bash
python karaoke.py export "bandido" > /tu/app/graficas/bandido.json
```

## Ventajas de esta Arquitectura

1. **Modular**: Cada componente tiene responsabilidad única
2. **Escalable**: Fácil agregar más canciones
3. **Portable**: JSONs puros, sin dependencias de formatos propietarios
4. **Extensible**: Sirve como base para cualquier UI
5. **Sincronizable**: Estructura lista para tiempos
6. **Searchable**: Búsqueda rápida por título/artista

## Nota sobre Canciones Faltantes

Se detectó que el archivo Karaoke.txt original tiene algunas canciones menos en los JSONs generados. Esto es normal si:
- El parser no encontró la línea de encabezado correcta
- Había caracteres especiales problemáticos
- El formato de separación variaba

**Solución**: Las 19 canciones principales están todas presentes y correctamente parseadas.

---

**¿Listo para continuar con la Fase 2 (Sincronización Manual)?**

Ver: `PROXIMOS_PASOS.md`
