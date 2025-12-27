"""
Script para crear un archivo MIDI de ejemplo
"""

import pretty_midi
from pathlib import Path


def create_sample_midi():
    """Crea un archivo MIDI de ejemplo simple"""
    
    # Crear objeto MIDI
    midi = pretty_midi.PrettyMIDI()
    
    # Establecer tempo (agregar una marca de tempo)
    midi.instruments_end_time = 5.0
    
    # Crear instrumento (ukulele = programa 24)
    instrument = pretty_midi.Instrument(program=24)
    
    # Notas para una escala simple (C mayor: C D E F G A)
    # Usando la afinación del ukulele: G C E A
    notes_data = [
        # (pitch_midi, start_time, duration)
        (60, 0.0, 0.5),    # C
        (62, 0.5, 0.5),    # D
        (64, 1.0, 0.5),    # E
        (65, 1.5, 0.5),    # F
        (67, 2.0, 0.5),    # G
        (69, 2.5, 0.5),    # A
        (71, 3.0, 0.5),    # B
        (72, 3.5, 1.0),    # C
    ]
    
    # Agregar notas al instrumento
    for pitch, start, duration in notes_data:
        note = pretty_midi.Note(velocity=100, pitch=pitch, start=start, end=start+duration)
        instrument.notes.append(note)
    
    # Agregar instrumento al MIDI
    midi.instruments.append(instrument)
    
    # Guardar archivo
    output_path = Path(__file__).parent.parent / "assets" / "midi" / "escala_ejemplo.mid"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    midi.write(str(output_path))
    print(f"✅ Archivo MIDI creado: {output_path}")


if __name__ == "__main__":
    create_sample_midi()
