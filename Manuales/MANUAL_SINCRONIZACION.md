# 🎯 Guía: Refinamiento Manual de Sincronización

## ¿Qué Acabamos de Hacer?

Ejecutamos análisis automático de audio en "Bandido.mp3" y generamos:
- **`bandido_sincronizada_auto.json`** - Tiempos automáticos

Los tiempos se distribuyeron basados en:
- Detección de cambios de energía en el audio
- Distribución proporcional a 26 líneas

**Duración detectada:** 181.23 segundos (~3 minutos)

---

## Ahora: Refinamiento Manual

El siguiente paso es **escuchar la canción y ajustar manualmente** los tiempos para mayor precisión.

### Paso 1: Abre el Editor de Sincronización

```bash
.\.venv\Scripts\python.exe sync_editor.py canciones/bandido_sincronizada_auto.json
```

### Paso 2: Opciones del Editor

Cuando se abra, verás un menú:

```
1. Ver letra completa con tiempos
2. Sincronizar línea por línea (manual)
3. Ajustar tiempo de una línea específica
4. Cargar tiempos desde archivo
5. Generar tiempos automáticos (estimado)
6. Guardar cambios
7. Salir
```

### Paso 3: Sincronización Óptima

**Recomendación:**

1. **Opción 1** - Ver la tabla completa para entender los tiempos actuales
2. **Opción 2** - Sincronizar escuchando:
   - Abre Audacity o tu reproductor favorito con el MP3
   - Reproducir la canción
   - En el editor, ingresa el tiempo exacto cuando comienza cada línea
   - El editor sugiere el tiempo actual (útil!)

3. **Opción 3** - Ajustar líneas problemáticas específicamente

4. **Opción 6** - Guardar cuando termines

---

## Método de Sincronización Manual (Detallado)

### Con Audacity (Recomendado)

1. Abre Audacity con `Bandido.mp3`
2. Reproducir (Spacebar)
3. Cuando llegues al momento exacto de una línea, **Pausa** (Spacebar)
4. Nota la posición en ms (aparece en la esquina)
5. En el editor de sincronización:
   ```
   Línea 1: [pausa] Da el tiempo → ingresa: 2438
   Línea 2: [pausa en segundo verso] → ingresa: 23545
   ...
   ```

### Con Reproductor + Excel

1. Abre un reproductor que muestre el tiempo (VLC, Foobar2000, etc.)
2. Toma nota en una hoja de cálculo con dos columnas:
   - Línea de letra
   - Tiempo en ms

3. Luego cargalo en el editor (opción 4)

---

## Tiempos Actuales vs. Esperado

Basado en la audición típica de "Bandido" (3:02 minutos):

| Línea | Automático | Probablemente Real | Diferencia |
|-------|-----------|-------------------|-----------|
| 1 | 2.44s | ~2-3s | ✓ Muy bien |
| 2 | 23.55s | ~20-25s | ⚠️ Podría variar |
| 3 | 42.17s | ~40-45s | ⚠️ Requiere revisión |
| ... | ... | ... | ... |

**La detección automática es una buena base, pero se beneficia de ajustes manuales.**

---

## Workflow Recomendado (30 minutos)

1. **Escucha completa** (3 min)
   - Reproducir la canción una vez para familiarizarte

2. **Ajuste de primeras 5 líneas** (5 min)
   - Más precisión es crítica al inicio

3. **Ajuste de resto** (15 min)
   - Línea por línea
   - O en secciones (estribillo, verso, etc.)

4. **Verificación final** (5 min)
   - Reproducir y verificar sincronización

5. **Guardar** (1 min)

**Total: ~30 minutos para una buena sincronización**

---

## Herramientas Recomendadas

### Para Ver Tiempos
- **Audacity** (Libre) - Excelente para ver waveform y tiempos
- **VLC** - Muestra tiempo durante reproducción
- **Foobar2000** - Muy preciso

### Para Editar JSON
- **VS Code** - Incluye el proyecto
- **Notepad++** - Ligero y rápido

---

## Comparar Después

Una vez sincronizado manualmente, puedes comparar:

```bash
.\.venv\Scripts\python.exe compare_sync.py \
  canciones/bandido_sincronizada_auto.json \
  -m canciones/bandido_sincronizada_manual.json
```

Esto mostrará las diferencias entre automático y manual.

---

## Ejemplo: Primeras 5 Líneas

```
Línea 1: "La luna me embrujó y me llevó hasta ti,"
  Automático: 2438ms (2.44s)
  Corrección: Escuchar exactamente cuando entra la voz
  ✓ Probablemente está bien

Línea 2: "veneno del amor que yo feliz bebí"
  Automático: 23545ms (23.55s)
  Corrección: ⚠️ Brecha de 21 segundos desde línea 1
            Probablemente es demasiado. Verificar audición.

Línea 3: "Y aunque mi pecho ardió y me abrasó la piel,"
  Automático: 42167ms (42.17s)
  ...
```

---

## Consejos Prácticos

✅ **Haz**
- Sincronizar en sesiones de 10 líneas máximo (menos fatiga)
- Usar auriculares de buena calidad
- Tomar descansos cada 30 min
- Guardar frecuentemente (cada 5-10 líneas)

❌ **No hagas**
- Sincronizar toda la canción de una vez (error acumulativo)
- Ignorar discrepancias grandes (> 500ms entre líneas)
- Sincronizar con prisa

---

## Próximos Pasos

### Fase 3: Interfaz Gráfica
Una vez sincronizada manualmente "Bandido", podrás:
1. Crear una app gráfica que lea el JSON
2. Reproducir con sincronización en tiempo real
3. Ver letras resaltadas según timing

### Ejemplo de Código (Pygame):
```python
import json
import pygame

cancion = json.load(open('bandido_sincronizada_manual.json'))
tiempo_actual = pygame.mixer.music.get_pos()

for linea in cancion['lineas']:
    if linea['tiempo'] <= tiempo_actual < linea['tiempo'] + 3000:
        mostrar_linea_resaltada(linea['texto'])
```

---

## ¿Preguntas?

- **¿Cómo sé si está bien sincronizado?**
  - Reproducir y verificar que la letra aparezca cuando la voz entra

- **¿Es tedioso?**
  - Sí, pero solo una vez. Luego tienes JSON reutilizable

- **¿Qué si cometo un error?**
  - El editor guarda versiones. Puedes revertir o ajustar individual.

- **¿Hay forma de acelerar?**
  - Sí: generar automático (hecho ✓), refinar solo secciones problemáticas

---

**¡Listo para sincronizar manualmente?**

Ejecuta:
```bash
.\.venv\Scripts\python.exe sync_editor.py canciones/bandido_sincronizada_auto.json
```

¡Diviértete! 🎤
