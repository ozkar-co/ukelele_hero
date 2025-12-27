"""
Herramienta para crear y guardar tablaturas configuradas
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from music.midi_loader import MIDILoader
from music.tablature_manager import TablatureManager


def main():
    """Herramienta interactiva para crear tablaturas guardadas"""
    
    print("\n" + "="*60)
    print("[TABLATURE CREATOR] CREADOR DE TABLATURAS GUARDADAS")
    print("="*60 + "\n")
    
    # Inicializar
    loader = MIDILoader()
    manager = TablatureManager()
    
    # Listar archivos MIDI
    midi_files = loader.get_midi_files()
    
    if not midi_files:
        print("❌ No hay archivos MIDI disponibles")
        return
    
    print("📁 Archivos MIDI disponibles:")
    for idx, filename in enumerate(midi_files, 1):
        print(f"   {idx}. {filename}")
    
    # Seleccionar MIDI
    while True:
        try:
            choice = input("\n🎵 Selecciona un archivo (1-{}): ".format(len(midi_files))).strip()
            choice = int(choice)
            if 1 <= choice <= len(midi_files):
                midi_file = midi_files[choice - 1]
                break
        except ValueError:
            pass
        print("❌ Opción inválida")
    
    # Cargar MIDI
    midi = loader.load_midi(midi_file)
    if not midi:
        return
    
    # Mostrar pistas
    tracks_info = loader.get_track_info(midi)
    print("\n📋 Pistas disponibles:")
    for info in tracks_info:
        print(f"   {info['index']}. {info['name']} ({info['note_count']} notas)")
    
    # Seleccionar pista
    while True:
        try:
            track = input(f"\n🎹 Selecciona pista (0-{len(tracks_info)-1}): ").strip()
            track = int(track)
            if 0 <= track < len(tracks_info):
                break
        except ValueError:
            pass
        print("❌ Opción inválida")
    
    # Extraer notas
    print(f"\n⏳ Procesando pista {track}...")
    notes = loader.get_track_notes(midi, track)
    
    if not notes:
        print("❌ No hay notas en esta pista")
        return
    
    # Mostrar rango
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    
    print(f"✅ Notas encontradas: {len(notes)}")
    print(f"Rango: {min_name} ({min_note}) a {max_name} ({max_note})")
    
    # Transposición
    print("\n" + "="*60)
    print("🎼 TRANSPOSICIÓN")
    print("="*60)
    print("Rango ukulele: C4 (60) a E6 (88)")
    
    octaves = None
    while True:
        try:
            oct_input = input("\n🎵 Octavas a transponer (-2 a +2, o auto): ").strip().lower()
            if oct_input == "auto":
                notes, octaves = loader.adjust_to_ukulele_range(notes)
                print(f"✅ Auto-ajustado: {octaves:+d} octava(s)")
                break
            else:
                octaves = int(oct_input)
                if -2 <= octaves <= 2:
                    if octaves != 0:
                        notes = loader.transpose_notes(notes, octaves)
                        print(f"✅ Transponido: {octaves:+d} octava(s)")
                    break
        except ValueError:
            pass
        print("❌ Entrada inválida")
    
    # Mostrar nuevo rango
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    print(f"Rango final: {min_name} ({min_note}) a {max_name} ({max_note})")
    
    # Guardar tablatura
    print("\n" + "="*60)
    print("💾 GUARDANDO TABLATURA")
    print("="*60)
    
    # Metadata personalizada
    description = input("\n📝 Descripción (opcional): ").strip()
    
    metadata = {
        "description": description,
        "created_by": "MIDI Tool"
    }
    
    # Guardar
    filename = manager.save_tablature(
        midi_filename=midi_file,
        track_index=track,
        notes=notes,
        octaves_transposed=octaves,
        tempo=120,
        metadata=metadata
    )
    
    print(f"\n✅ ¡Tablatura guardada exitosamente!")
    print(f"Archivo: {filename}")
    
    # Mostrar preview
    show_preview = input("\n¿Ver preview de datos? (s/n): ").strip().lower()
    
    if show_preview == 's':
        print("\n" + "="*60)
        print("PREVIEW - Datos para UI")
        print("="*60 + "\n")
        
        tab_data = manager.load_tablature(filename)
        ui_data = manager.export_to_ui_format(tab_data)
        
        import json
        print(json.dumps(ui_data, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
