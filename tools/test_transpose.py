"""
Script de prueba para transposición con archivo más complejo
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from music.midi_loader import MIDILoader
from music.tablature_generator import UkuleleTableGenerator


def main():
    # Cargar MIDI
    loader = MIDILoader()
    midi_files = loader.get_midi_files()
    
    print(f"\nArchivos disponibles: {midi_files}")
    
    # Usar el segundo archivo si existe
    midi_file = midi_files[1] if len(midi_files) > 1 else midi_files[0]
    
    print(f"\nCargando: {midi_file}")
    midi = loader.load_midi(midi_file)
    
    if not midi:
        return
    
    # Extraer notas
    notes = loader.get_track_notes(midi, 0)
    
    print("\n" + "="*60)
    print("RANGO ORIGINAL")
    print("="*60)
    
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    
    print(f"Rango: {min_name} ({min_note}) a {max_name} ({max_note})")
    print(f"Rango ukulele: C4 (60) a E6 (88)")
    
    # Auto-ajustar
    adjusted_notes, octaves = loader.adjust_to_ukulele_range(notes)
    
    print(f"\n✅ Auto-ajuste: {octaves:+d} octava(s)")
    
    min_note, max_note = loader.get_notes_range(adjusted_notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    print(f"Nuevo rango: {min_name} ({min_note}) a {max_name} ({max_note})")
    
    # Tablatura
    generator = UkuleleTableGenerator()
    tab = generator.generate_tab_from_notes(adjusted_notes)
    print("\n" + tab)


if __name__ == "__main__":
    main()
