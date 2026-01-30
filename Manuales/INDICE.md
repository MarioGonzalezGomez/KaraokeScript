# 📚 ÍNDICE COMPLETO - KaraokeScript

## Documentos (Léelos en Este Orden)

### 1️⃣ **QUICKSTART.md** ⭐ COMIENZA AQUÍ
- Guía de 5 minutos
- Primeros pasos básicos
- Solución rápida de problemas
- **Tiempo estimado: 5 minutos**

### 2️⃣ **README.md** 
- Documentación completa del CLI
- Todos los comandos disponibles
- Formato JSON explicado
- Próximas fases
- **Tiempo estimado: 15 minutos**

### 3️⃣ **PROYECTO_RESUMEN.md**
- Visión general del proyecto
- Qué se creó y por qué
- Características actuales
- Ventajas arquitectura
- **Tiempo estimado: 10 minutos**

### 4️⃣ **PROXIMOS_PASOS.md**
- Guía de fases futuras (2-4)
- Alternativas de sincronización
- Interfaces gráficas propuestas
- Librerías recomendadas
- **Tiempo estimado: 20 minutos**

### 5️⃣ **EJEMPLOS_INTEGRACION.md**
- 6 ejemplos de código práctico
- CLI personalizada
- API REST
- Pygame visualizador
- **Tiempo estimado: 30 minutos**

---

## Scripts Python (Ejecuta Estos)

### 🎵 **karaoke.py** ⭐ PRINCIPAL
**Aplicación CLI para gestionar canciones**

```bash
# Ver todas las canciones
python karaoke.py list

# Ver letra de una canción
python karaoke.py show "<nombre>"

# Buscar canciones
python karaoke.py search "<término>"

# Información detallada
python karaoke.py info "<nombre>"

# Exportar JSON
python karaoke.py export "<nombre>"
```

**Comandos disponibles:**
- `list` - Listar todas las canciones
- `show` - Mostrar letra completa
- `search` - Buscar por título/artista
- `info` - Info con tiempos actuales
- `export` - Exportar JSON puro

---

### ⏱️ **sync_editor.py**
**Editor interactivo para sincronizar tiempos**

```bash
# Sincronizar una canción
python sync_editor.py canciones/bandido.json
```

**Menú del editor:**
1. Ver letra con tiempos
2. Sincronizar línea por línea
3. Ajustar tiempo específico
4. Cargar tiempos desde archivo
5. Generar tiempos automáticos
6. Guardar cambios
7. Salir

---

### 🔧 **parser_karaoke.py**
**Parser de Karaoke.txt a JSONs**

```bash
# Regenerar JSONs desde texto
python parser_karaoke.py
```

**Función:**
- Lee Karaoke.txt
- Extrae título, artista y letra
- Crea 19 archivos JSON individuales

---

## Carpetas

### 📂 **canciones/**
Contiene 19 archivos JSON:
```
canciones/
├── 20_de_enero.json
├── a_quien_le_importa.json
├── bailar_pegados.json
├── bandido.json
├── caliente.json
├── como_una_ola.json
├── corazón_contento.json
├── cuando_tú_vas.json
├── dile_que_la_quiero.json
├── esa_diva.json
├── europes_living_a_celebration.json
├── nochentera.json
├── obsesión.json
├── olvídame_y_pega_la_vuelta.json
├── raffaella.json
├── sobreviviré.json
├── vivir_así_es_morir_de_amor.json
├── vivo_cantando.json
└── y_yo_te_besé.json
```

Cada JSON tiene la estructura:
```json
{
  "id": número,
  "titulo": "NOMBRE",
  "artista": "AUTOR",
  "duracion": 0,
  "lineas": [
    {"tiempo": 0, "texto": "..."}
  ]
}
```

---

## Ejemplos

### 📋 **EJEMPLO_BANDIDO_SINCRONIZADO.json**
- Ejemplo de canción CON tiempos sincronizados
- Muestra cómo debe verse una canción lista
- Valores de tiempo en milisegundos

---

## Archivos de Datos

### 📄 **Karaoke.txt**
- Archivo original con 19 canciones
- Formato: `"TITULO" ARTISTA` + letra
- 46 KB, ~1650 líneas
- Usado por parser_karaoke.py

---

## Estadísticas del Proyecto

| Métrica | Valor |
|---------|-------|
| Canciones parseadas | 19 |
| Líneas de letra | ~850 |
| Archivos JSON | 19 |
| Scripts Python | 3 |
| Documentos | 6 |
| Tamaño total | ~170 KB |
| Líneas de código | ~2500+ |

---

## Roadmap (Fases Futuras)

### 📍 Fase 2: Sincronización Manual (AHORA)
- Usar `sync_editor.py` con MP3s
- Sincronizar escuchando
- Guardar tiempos en JSONs

### 📍 Fase 3: Interfaz Gráfica (Próximo)
- Mostrar letra sincronizada
- Pygame, PyQt, o Web
- Ver `EJEMPLOS_INTEGRACION.md`

### 📍 Fase 4: Reproducción (Avanzado)
- Controls (play, pause, seek)
- Stats y rankings
- Almacenamiento de configuración

---

## Comandos Rápidos

```bash
# Ver todas las canciones
python karaoke.py list

# Ver letra
python karaoke.py show "bandido"

# Buscar artista
python karaoke.py search "alaska"

# Sincronizar
python sync_editor.py canciones/bandido.json

# Exportar para tu app
python karaoke.py export "obsesión" > obsesion.json

# Regenerar JSONs
python parser_karaoke.py
```

---

## Estructura del Proyecto

```
KaraokeScript/
│
├── 📚 DOCUMENTACIÓN
│   ├── QUICKSTART.md              ← COMIENZA AQUÍ
│   ├── README.md
│   ├── PROYECTO_RESUMEN.md
│   ├── PROXIMOS_PASOS.md
│   ├── EJEMPLOS_INTEGRACION.md
│   └── INDICE.md                  ← Este archivo
│
├── 🐍 SCRIPTS PYTHON
│   ├── karaoke.py                 ← Aplicación principal
│   ├── parser_karaoke.py
│   └── sync_editor.py
│
├── 🎵 DATOS
│   ├── Karaoke.txt                ← Archivo original
│   ├── canciones/                 ← 19 JSONs
│   └── EJEMPLO_BANDIDO_SINCRONIZADO.json
│
└── 📋 ESTE ARCHIVO
    └── INDICE.md
```

---

## Cómo Usar Este Índice

1. **Para empezar:** Abre `QUICKSTART.md`
2. **Para entender:** Lee `README.md` y `PROYECTO_RESUMEN.md`
3. **Para próximas fases:** Consulta `PROXIMOS_PASOS.md`
4. **Para código:** Ve `EJEMPLOS_INTEGRACION.md`
5. **Para referencia:** Este archivo (`INDICE.md`)

---

## Respuestas Rápidas

### ¿Cómo veo todas las canciones?
```bash
python karaoke.py list
```

### ¿Cómo veo una canción específica?
```bash
python karaoke.py show "nombre"
```

### ¿Cómo sincronizo tiempos?
```bash
python sync_editor.py canciones/nombre.json
```

### ¿Cómo exporto JSON para mi app?
```bash
python karaoke.py export "nombre" > salida.json
```

### ¿Dónde veo ejemplos de código?
Ver `EJEMPLOS_INTEGRACION.md`

### ¿Qué hago en la siguiente fase?
Ver `PROXIMOS_PASOS.md`

---

## Contacto / Ayuda

Si tienes dudas:
1. Lee la documentación correspondiente en este índice
2. Busca en `EJEMPLOS_INTEGRACION.md`
3. Consulta `README.md`
4. Revisa `PROXIMOS_PASOS.md` para orientación

---

## Versión

**KaraokeScript v1.0**
- Parseador de canciones ✅
- CLI de gestión ✅
- Editor de sincronización ✅
- Base para apps gráficas ✅
- Documentación completa ✅

**Próxima versión:**
- Sincronización automática
- UI gráfica integrada
- Reproducción en tiempo real

---

**¡Listo para comenzar? Abre `QUICKSTART.md`** 🚀
