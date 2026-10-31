"""
Afinación estándar del ukulele soprano (GCEA) y conversiones cuerda/traste.
"""

STRING_ORDER = ("G", "C", "E", "A")

# MIDI: C4 = 60, G4 = 67.
OPEN_STRING_PITCHES = {
    "G": 67,
    "C": 60,
    "E": 64,
    "A": 69,
}

MAX_FRET = 20

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def pitch_to_note_name(pitch):
    """Convierte un pitch MIDI a nombre de nota, por ejemplo 60 -> 'C4'."""
    octave = (pitch // 12) - 1
    return f"{NOTE_NAMES[pitch % 12]}{octave}"


def string_fret_to_pitch(string_name, fret):
    """Devuelve el pitch MIDI de una cuerda y traste, o None si no es válido."""
    if string_name not in OPEN_STRING_PITCHES:
        return None
    if fret < 0 or fret > MAX_FRET:
        return None
    return OPEN_STRING_PITCHES[string_name] + fret


def pitch_to_string_fret(pitch, max_fret=MAX_FRET):
    """
    Busca la posición más sencilla para un pitch MIDI.

    Devuelve (cuerda, traste) eligiendo el traste más bajo y, en empate,
    el orden G-C-E-A. Devuelve (None, None) si el pitch queda fuera del rango.
    """
    candidates = []

    for order, string_name in enumerate(STRING_ORDER):
        fret = pitch - OPEN_STRING_PITCHES[string_name]
        if 0 <= fret <= max_fret:
            candidates.append((fret, order, string_name))

    if not candidates:
        return None, None

    fret, _, string_name = min(candidates)
    return string_name, fret
