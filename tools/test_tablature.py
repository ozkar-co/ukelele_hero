"""
Script de prueba para ver la tablatura completa
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from music.midi_loader import MIDILoader
from music.tablature_generator import UkuleleTableGenerator


def main():
    # Cargar el MIDI de ejemplo
    loader = MIDILoader()
    midi = loader.load_midi('escala_ejemplo')
    
    if not midi:
        return
    
    # Extraer notas de la pista 0
    notes = loader.get_track_notes(midi, 0)
    
    # Mostrar información de rango
    print("\n" + "="*60)
    print("INFORMACIÓN DE NOTAS")
    print("="*60)
    
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    
    print(f"Rango original: {min_name} ({min_note}) a {max_name} ({max_note})")
    print(f"Rango ukulele: C4 (60) a E6 (88)")
    
    # Auto-ajustar a rango del ukulele
    adjusted_notes, octaves = loader.adjust_to_ukulele_range(notes)
    if octaves != 0:
        print(f"✅ Auto-ajustado: {octaves:+d} octava(s)")
        notes = adjusted_notes
    else:
        print("✅ Las notas ya están en el rango")
    
    # Mostrar nuevo rango
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    print(f"Rango final: {min_name} ({min_note}) a {max_name} ({max_note})")
    
    # Generar y mostrar tablatura
    generator = UkuleleTableGenerator()
    
    print("\n" + "="*60)
    print("📊 TABLATURA SIMPLE")
    print("="*60 + "\n")
    print(generator.generate_simple_tab(notes))
    
    print("\n" + "="*60)
    print("📊 TABLATURA COMPLETA")
    print("="*60 + "\n")
    print(generator.generate_tab_from_notes(notes))


if __name__ == "__main__":
    main()
