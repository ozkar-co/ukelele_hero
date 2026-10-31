# Uso y controles

## Menú principal

| Opción | Función |
|---|---|
| Modo Juego | Tablatura con puntuación y validación de pitch |
| Entrenador | Práctica guiada nota a nota |
| Escuchar Canción | Reproduce la tablatura y muestra las notas |
| Detector de Notas | Afinador y análisis en tiempo real |
| Calibrar Micrófono | Ajusta los umbrales al micrófono y la sala |

## Modo Juego

- Las notas se desplazan de derecha a izquierda sobre las cuerdas A, E, C y G.
- La nota debe coincidir con el pitch detectado dentro de la ventana de golpeo.
- `ESPACIO`: pausa.
- `ESC`: volver al menú.

La ventana de acierto es de ±200 ms. Una nota sostenida no acierta dos notas
seguidas con el mismo pitch; hace falta un pequeño silencio entre ambas.

## Entrenador

- La línea de tiempo queda congelada en la nota actual.
- Avanza cuando detecta la nota pedida.
- Muestra la cuerda y el traste correctos.
- `ESPACIO`: saltar nota.
- `R`: reiniciar canción.
- `ESC`: volver al menú.

## Escuchar Canción

- Reproduce los tonos de la tablatura mientras las notas se desplazan.
- No usa micrófono.
- `ESPACIO`: pausa.
- `R`: reiniciar.
- `ESC`: volver al menú.

## Detector de Notas

- `ESPACIO`: pausar o reanudar la detección.
- `ESC`: volver al menú.

## Calibración

1. Mide el ruido de sala en silencio.
2. Pide diez notas indicando cuerda y traste.
3. Calcula `min_volume`, `min_confidence` y `note_tolerance_cents`.
4. Guarda un perfil nuevo en `assets/calibration/`.

- `ESPACIO`: repetir la nota actual.
- `ENTER`: saltar la nota actual.
- `R`: reiniciar la calibración.
- `ESC`: cancelar.

El perfil más reciente se carga automáticamente en todos los modos.
Los perfiles son datos locales y están excluidos de git.

## Variantes de tablatura

El generador guarda archivos separados:

```
cancion_track0_oct+1_normal.json
cancion_track0_oct+1_easy.json
```

La variante `easy` es monofónica y tiene menos notas. El modo Escucha
sirve para comparar ambas antes de jugarlas.
