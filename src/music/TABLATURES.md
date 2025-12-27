# 💾 Gestor de Tablaturas

## Descripción

Sistema para guardar y cargar tablaturas configuradas en formato JSON, listo para integración en la UI del juego.

## Componentes

### `TablatureManager`
Gestiona la serialización y almacenamiento de tablaturas:

```python
from src.music.tablature_manager import TablatureManager

manager = TablatureManager()

# Guardar una tablatura
filename = manager.save_tablature(
    midi_filename="mi_cancion",
    track_index=0,
    notes=[(60, 0.0, 0.5), ...],
    octaves_transposed=0,
    tempo=120,
    metadata={"description": "Mi primera tablatura"}
)

# Cargar una tablatura
tab_data = manager.load_tablature("mi_cancion_track0_oct+0")

# Convertir a formato UI
ui_data = manager.export_to_ui_format(tab_data)
```

### `GameTablatureLoader`
API simplificada para usar en la UI del juego:

```python
from tools.test_game_integration import GameTablatureLoader

loader = GameTablatureLoader()

# Listar todas las tablaturas
tabs = loader.list_available_tablatures()

# Cargar una tablatura
data = loader.load_tablature_for_game("escala_ejemplo_track0_oct+0")

# Obtener notas de una cuerda
notas_a = loader.get_notes_for_string('A')

# Obtener todas las notas ordenadas por tiempo
todas_las_notas = loader.get_all_notes_sorted_by_time()

# Obtener información de la tablatura
info = loader.get_tablature_info()
```

## Formato de Almacenamiento

Las tablaturas se guardan en JSON con la siguiente estructura:

```json
{
  "version": "1.0",
  "source": {
    "midi_file": "escala_ejemplo",
    "track_index": 0
  },
  "configuration": {
    "octaves_transposed": 0,
    "tempo": 120
  },
  "notes": [
    {
      "pitch": 60,
      "start_time": 0.0,
      "end_time": 0.5,
      "note_name": "C4"
    }
  ],
  "statistics": {
    "total_notes": 8,
    "duration": 4.5,
    "min_pitch": 60,
    "max_pitch": 72
  },
  "metadata": {
    "description": "Mi primera tablatura"
  }
}
```

## Formato para la UI

Las tablaturas se convierten a este formato para la UI:

```json
{
  "source": "escala_ejemplo",
  "track": 0,
  "tempo": 120,
  "octaves_transposed": 0,
  "strings": {
    "G": [
      {
        "fret": 7,
        "pitch": 67,
        "note": "G4",
        "start_time": 2.0,
        "end_time": 2.5,
        "duration": 0.5
      }
    ],
    "C": [...],
    "E": [...],
    "A": [...]
  },
  "statistics": {
    "total_notes": 8,
    "duration": 4.5,
    "min_pitch": 60,
    "max_pitch": 72
  },
  "total_notes": 8
}
```

## Estructura de Carpetas

```
assets/
├── midi/
│   ├── escala_ejemplo.mid
│   └── saria_song.mid
└── tablatures/
    ├── escala_ejemplo_track0_oct+0.json
    ├── saria_song_track0_oct+0.json
    └── ...
```

## Flujo de Uso

### 1. Crear una Tablatura Configurada

```bash
python tools/create_tablature.py
```

Proceso interactivo:
- Seleccionar archivo MIDI
- Seleccionar pista
- Configurar transposición (automática o manual)
- Agregar descripción
- Guardar en JSON

### 2. Cargar en la UI del Juego

```python
from tools.test_game_integration import GameTablatureLoader

loader = GameTablatureLoader()
game_data = loader.load_tablature_for_game("escala_ejemplo_track0_oct+0")

# Usar en el juego
for string_name in ['G', 'C', 'E', 'A']:
    notes = loader.get_notes_for_string(string_name)
    # Renderizar en pantalla
```

### 3. Acceder a Datos Específicos

```python
# Obtener info general
info = loader.get_tablature_info()
print(f"Tempo: {info['tempo']} BPM")
print(f"Duración: {info['duration']}s")

# Obtener notas en orden temporal (para animación)
notas_timeline = loader.get_all_notes_sorted_by_time()

# Obtener notas de una cuerda (para renderizado específico)
notas_cuerda_a = loader.get_notes_for_string('A')
```

## Métodos Principales

### `TablatureManager`

```python
# Guardar
save_tablature(midi_filename, track_index, notes, octaves_transposed, tempo, metadata)

# Cargar
load_tablature(filename)

# Listar
get_saved_tablatures()

# Eliminar
delete_tablature(filename)

# Convertir formato
export_to_ui_format(tablature_data)
```

### `GameTablatureLoader`

```python
# Listar disponibles
list_available_tablatures()

# Cargar para juego
load_tablature_for_game(tablature_name)

# Acceder a datos
get_notes_for_string(string_name)
get_all_notes_sorted_by_time()
get_tablature_info()
```

## Ejemplo Completo

```python
from tools.test_game_integration import GameTablatureLoader

# Inicializar cargador
loader = GameTablatureLoader()

# Obtener lista de tablaturas disponibles
available = loader.list_available_tablatures()

# Cargar una tablatura
tablature = loader.load_tablature_for_game(available[0])

# Obtener información
info = loader.get_tablature_info()
print(f"Tocando: {info['source']} a {info['tempo']} BPM")

# Renderizar notas en timeline
timeline = loader.get_all_notes_sorted_by_time()
for note in timeline:
    print(f"Traste {note['fret']} en {note['start_time']:.2f}s")
```

## Próximas Mejoras

- [ ] Exportar a formato ASCII para impresión
- [ ] Sistema de favoritos/etiquetas
- [ ] Búsqueda y filtrado de tablaturas
- [ ] Versioning de tablaturas
- [ ] Exportar a PDF
- [ ] Sincronización con servidor

---

**Estado**: ✅ Funcional y lista para integración en UI

