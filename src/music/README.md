# 🎸 Módulo MIDI & Tablatura

## Descripción

Módulo para cargar archivos MIDI y generar tablaturas para ukulele. Este módulo es esencial para la **Etapa 2 y 3** del proyecto (Juego completo).

## Características

### 📁 `MIDILoader`
- Carga archivos MIDI desde carpeta `assets/midi/`
- Extrae información de pistas (nombre, instrumento, duración)
- Filtra notas dentro del rango del ukulele
- Convierte notas MIDI a nombres y frecuencias

### 🎼 `UkuleleTableGenerator`
- Genera tablaturas a partir de notas MIDI
- Mapea automáticamente pitch MIDI a trastes del ukulele
- Soporta afinación estándar GCEA
- Genera tablaturas simples (lista de trastes) y completas (ASCII)

## Uso

### Cargar un MIDI

```python
from src.music.midi_loader import MIDILoader

# Inicializar cargador
loader = MIDILoader()

# Listar archivos disponibles
archivos = loader.get_midi_files()
print(archivos)  # ['cancion1', 'cancion2', ...]

# Cargar un archivo
midi = loader.load_midi('cancion1')

# Obtener información de pistas
tracks_info = loader.get_track_info(midi)

# Extraer notas de la pista 0
notas = loader.get_track_notes(midi, track_index=0)
# Retorna: [(pitch, start_time, end_time), ...]
```

### Generar Tablatura

```python
from src.music.tablature_generator import UkuleleTableGenerator

generator = UkuleleTableGenerator()

# Generar tablatura simple
tab_simple = generator.generate_simple_tab(notas)
print(tab_simple)

# Generar tablatura completa
tab_completa = generator.generate_tab_from_notes(notas, tempo=120)
print(tab_completa)
```

### Usar la Herramienta MIDI CLI

```bash
python tools/midi_tool.py
```

Interfaz interactiva para:
1. Listar archivos MIDI disponibles
2. Seleccionar y cargar un archivo
3. Ver información de pistas
4. Generar tablaturas

## Estructura de Archivos

```
assets/
└── midi/
    ├── escala_ejemplo.mid     (MIDI de prueba)
    ├── tu_cancion.mid         (Agregar tus archivos aquí)
    └── otra_cancion.mid

tools/
├── midi_tool.py              (CLI interactiva)
└── create_sample_midi.py     (Crear MIDIs de ejemplo)

src/music/
├── __init__.py
├── midi_loader.py            (Cargador MIDI)
└── tablature_generator.py    (Generador de tablaturas)
```

## Afinación del Ukulele

El módulo usa la afinación estándar GCEA:

```
4ª cuerda: A4 (69 Hz en MIDI)
3ª cuerda: E4 (64 Hz)
2ª cuerda: C4 (60 Hz)
1ª cuerda: G4 (67 Hz)
```

## Rango Soportado

- **Rango MIDI**: C2 (36) a E6 (88)
- **Trastes**: 0 a 20 por cuerda

## API Reference

### `MIDILoader`

```python
loader = MIDILoader(midi_folder="path/to/folder")

# Métodos
loader.get_midi_files() -> List[str]
loader.load_midi(filename: str) -> PrettyMIDI
loader.get_track_info(midi: PrettyMIDI) -> List[Dict]
loader.get_track_notes(midi: PrettyMIDI, track_index: int) -> List[Tuple]

# Estáticos
MIDILoader.midi_note_to_name(pitch: int) -> str
MIDILoader.midi_note_to_frequency(pitch: int) -> float
```

### `UkuleleTableGenerator`

```python
generator = UkuleleTableGenerator()

# Métodos
generator.generate_tab_from_notes(notes, tempo=120) -> str
generator.generate_simple_tab(notes) -> str
```

## Próximas Mejoras

- [ ] Soporte para múltiples afinaciones (DGBE, etc.)
- [ ] Exportar tablaturas a formato ASCII/PDF
- [ ] Detectar patrones rítmicos
- [ ] Simplificar tablaturas complejas
- [ ] Integración con UI del juego

## Ejemplo Completo

```python
from src.music.midi_loader import MIDILoader
from src.music.tablature_generator import UkuleleTableGenerator

# Cargar MIDI
loader = MIDILoader()
midi = loader.load_midi('mi_cancion')

# Extraer pista
notas = loader.get_track_notes(midi, track_index=0)

# Generar tablatura
generator = UkuleleTableGenerator()
tablatura = generator.generate_simple_tab(notas)

print(tablatura)
```

---

**Estado**: ✅ Funcional y listo para integración

