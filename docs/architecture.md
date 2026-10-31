# Arquitectura

## Estructura

```
main.py                  Único punto de entrada
src/
  audio/                 Micrófono, FFT, detección y perfiles
  game/                  Modos: juego, entrenador, escucha, afinador, calibración
    ui/                  Componentes visuales y estilos compartidos
  music/                 MIDI, tablaturas, afinación y simplificación
  utils/                 Configuración y helpers
assets/                  MIDI, tablaturas y perfiles de calibración
tools/                   Generador de tablaturas (herramienta de depuración)
tests/                   Tests unitarios
docs/                    Documentación
```

## Imports

`main.py` agrega `src/` a `sys.path` y los módulos se importan sin el prefijo
`src.` (`from game.tablature_mode import ...`). Los tests usan `PYTHONPATH=src`.

## Componente visual

`src/game/ui/tablature_view.py` dibuja cuerdas, zona de golpeo y notas.
`src/game/ui/styles.py` centraliza colores, dimensiones, orden visual de
cuerdas y ventana de acierto. Juego, entrenador y escucha usan el mismo
componente; no duplicar estilos en los modos.

`StringFretDisplay` reutiliza los colores y el orden de cuerdas de `styles.py`
para el panel de trastes del afinador.

## Audio

```
Micrófono -> FrequencyAnalyzer -> NoteDetector -> modo
```

`NoteDetector` carga el perfil de calibración más reciente y aplica
`min_volume`, `min_confidence`, `note_tolerance_cents` y `history_size`.
El análisis de frecuencia usa FFT con interpolación parabólica.

## Tablaturas

`TablatureManager` lee y escribe JSON en `assets/tablatures/`.
`MIDILoader` extrae notas y elige la octava automáticamente.
`simplifier.py` genera la variante easy.
Ver [pipeline MIDI](midi.md).

## Tests

```bash
make test
```

Los tests cubren análisis de audio, detección, calibración, perfiles,
mapeo cuerda/traste, octava automática, simplificación y validación de notas.
