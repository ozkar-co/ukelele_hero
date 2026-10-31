# Ukulele Hero

Juego y entrenador de ukulele con pygame, tablaturas MIDI y detección de notas por micrófono.

## Modos

- **Juego**: notas en movimiento, puntuación y validación de la nota tocada.
- **Entrenador**: espera la nota indicada (cuerda y traste) antes de avanzar.
- **Escucha**: reproduce la tablatura con tonos sintetizados mientras muestra las notas.
- **Detector de notas**: afinador y análisis en tiempo real.
- **Calibración**: ajusta los umbrales al micrófono y al ruido de la sala.

## Inicio rápido

```bash
make config
.venv/bin/python main.py
```

Requiere PortAudio (`sudo apt install portaudio19-dev`).
`make dist` genera un bundle portable.

## Documentación

- [Instalación](docs/install.md)
- [Uso y controles](docs/usage.md)
- [Arquitectura](docs/architecture.md)
- [Pipeline MIDI y variantes](docs/midi.md)
- [Distribución](docs/distribution.md)
