"""
Herramienta CLI para cargar MIDI y mostrar tablatura
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from music.midi_loader import MIDILoader
from music.tablature_generator import UkuleleTableGenerator


def main():
    """Interfaz principal de la herramienta MIDI"""
    
    print("\n" + "="*60)
    print("🎸 HERRAMIENTA MIDI PARA UKULELE HERO")
    print("="*60 + "\n")
    
    # Inicializar cargador MIDI
    loader = MIDILoader()
    tab_generator = UkuleleTableGenerator()
    
    # Listar archivos disponibles
    midi_files = loader.get_midi_files()
    
    if not midi_files:
        print("❌ No hay archivos MIDI en la carpeta assets/midi/")
        print("\n💡 Coloca archivos .mid o .midi en la carpeta:")
        print("   ukelele_hero/assets/midi/")
        return
    
    print(f"📁 Archivos MIDI disponibles ({len(midi_files)}):")
    for idx, filename in enumerate(midi_files, 1):
        print(f"   {idx}. {filename}")
    
    print("\n" + "="*60)
    
    # Pedir selección del usuario
    while True:
        try:
            choice = input("\n🎵 Selecciona un número de archivo (0 para salir): ").strip()
            
            if choice == "0":
                print("👋 ¡Hasta luego!")
                return
            
            choice = int(choice)
            if 1 <= choice <= len(midi_files):
                selected_file = midi_files[choice - 1]
                break
            else:
                print("❌ Opción inválida. Intenta de nuevo.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")
    
    # Cargar el MIDI
    print(f"\n⏳ Cargando {selected_file}...")
    midi = loader.load_midi(selected_file)
    
    if not midi:
        return
    
    # Mostrar información de pistas
    print("\n" + "="*60)
    print("📋 INFORMACIÓN DE PISTAS")
    print("="*60)
    
    tracks_info = loader.get_track_info(midi)
    
    for info in tracks_info:
        print(f"\nPista {info['index']}: {info['name']}")
        print(f"  • Programa: {info['program']}")
        print(f"  • Es Batería: {'Sí' if info['is_drum'] else 'No'}")
        print(f"  • Notas: {info['note_count']}")
        print(f"  • Duración: {info['start_time']:.2f}s - {info['end_time']:.2f}s")
    
    # Seleccionar pista
    print("\n" + "="*60)
    track_choice = 0
    
    if len(tracks_info) > 1:
        while True:
            try:
                tc = input(f"\n🎹 Selecciona pista (0-{len(tracks_info)-1}, por defecto 0): ").strip()
                if tc == "":
                    track_choice = 0
                    break
                tc = int(tc)
                if 0 <= tc < len(tracks_info):
                    track_choice = tc
                    break
                else:
                    print("❌ Opción inválida.")
            except ValueError:
                print("❌ Por favor ingresa un número válido.")
    
    # Extraer notas
    print(f"\n⏳ Extrayendo notas de la pista {track_choice}...")
    notes = loader.get_track_notes(midi, track_choice)
    
    if not notes:
        print("❌ No hay notas en esta pista")
        return
    
    print(f"✅ Se encontraron {len(notes)} notas\n")
    
    # Mostrar rango de notas
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    print(f"Rango de notas: {min_name} ({min_note}) a {max_name} ({max_note})")
    print(f"Rango ukulele: C4 (60) a E6 (88)")
    
    # Ajuste de octavas
    print("\n" + "="*60)
    octave_choice = None
    
    while True:
        try:
            oc = input("\n🎵 Octavas a transponer (-2 a +2, Enter para auto): ").strip()
            if oc == "":
                # Auto-ajustar
                notes, octaves_applied = loader.adjust_to_ukulele_range(notes)
                if octaves_applied != 0:
                    print(f"✅ Auto-ajustado: {octaves_applied:+d} octava(s)")
                else:
                    print("✅ Las notas ya están en el rango del ukulele")
                break
            else:
                octave_choice = int(oc)
                if -2 <= octave_choice <= 2:
                    if octave_choice != 0:
                        notes = loader.transpose_notes(notes, octave_choice)
                        print(f"✅ Notas transponidas: {octave_choice:+d} octava(s)")
                    break
                else:
                    print("❌ Por favor ingresa un número entre -2 y +2.")
        except ValueError:
            print("❌ Por favor ingresa un número válido.")
    
    # Mostrar nuevo rango después de transposición
    min_note, max_note = loader.get_notes_range(notes)
    min_name = loader.midi_note_to_name(min_note)
    max_name = loader.midi_note_to_name(max_note)
    print(f"Nuevo rango: {min_name} ({min_note}) a {max_name} ({max_note})")
    
    # Mostrar tablatura
    print("\n" + "="*60)
    print("GENERANDO TABLATURA...")
    print("="*60 + "\n")
    
    # Mostrar tablatura simple primero
    simple_tab = tab_generator.generate_simple_tab(notes)
    print(simple_tab)
    
    # Opción de ver tablatura completa
    print("\n" + "="*60)
    show_full = input("\n¿Mostrar tablatura completa? (s/n): ").strip().lower()
    
    if show_full == 's':
        full_tab = tab_generator.generate_tab_from_notes(notes, tempo=120)
        print(full_tab)
    
    print("\n✅ ¡Herramienta completada!")


if __name__ == "__main__":
    main()
