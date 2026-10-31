"""
Utilidades para generar variantes simplificadas de una tablatura.

Trabajan con notas en formato (pitch, start_time, end_time) y no escriben
archivos; el generador de herramientas decide qué variantes guardar.
"""

from .ukelele import MAX_FRET, pitch_to_string_fret


PLAYABLE_MIN = 60
PLAYABLE_MAX = 88


def _group_onsets(notes, tolerance=0.05):
    groups = []
    for note in sorted(notes, key=lambda item: (item[1], item[0])):
        if groups and abs(note[1] - groups[-1][0][1]) <= tolerance:
            groups[-1].append(note)
        else:
            groups.append([note])
    return groups


def filter_playable(notes, max_fret=MAX_FRET):
    """Conserva solo notas que existen en GCEA dentro del mástil."""
    playable = []
    for note in notes:
        pitch = note[0]
        if not (PLAYABLE_MIN <= pitch <= PLAYABLE_MAX):
            continue
        string_name, _fret = pitch_to_string_fret(pitch, max_fret)
        if string_name is not None:
            playable.append(note)
    return playable


def skyline(notes):
    """Deja la nota más aguda de cada ataque (melodía aproximada)."""
    return [max(group, key=lambda note: note[0]) for group in _group_onsets(notes)]


def remove_valleys(notes, min_drop=4):
    """
    Elimina notas claramente por debajo de sus dos vecinas.

    En arpegios de guitarra esto quita el acompañamiento que queda como nota
    aguda entre dos notas de la melodía. Puede quitar notas de paso reales,
    por eso el umbral es configurable.
    """
    if len(notes) < 3:
        return list(notes)

    result = [notes[0]]
    for index in range(1, len(notes) - 1):
        previous, current, following = notes[index - 1], notes[index], notes[index + 1]
        is_valley = (
            current[0] <= previous[0] - min_drop
            and current[0] <= following[0] - min_drop
        )
        if not is_valley:
            result.append(current)
    result.append(notes[-1])
    return result


def limit_to_beat(notes, bpm, subdivision=1.0):
    """
    Conserva como máximo una nota por pulso.

    subdivision=1 -> una por negra; 2 -> una por corchea. De cada pulso se
    queda la nota más aguda.
    """
    if not notes or bpm <= 0:
        return list(notes)

    step = (60.0 / bpm) / subdivision
    chosen = {}
    for note in notes:
        beat = int(note[1] / step)
        if beat not in chosen or note[0] > chosen[beat][0]:
            chosen[beat] = note

    result = []
    for beat in sorted(chosen):
        pitch, start, end = chosen[beat]
        max_end = start + (step * 0.9)
        result.append((pitch, start, min(end, max_end)))
    return result


def simplify_easy(notes, bpm, subdivision=1.0, min_drop=4):
    """Melodía monofónica y cómoda para practicar."""
    simplified = skyline(notes)
    simplified = remove_valleys(simplified, min_drop=min_drop)
    simplified = limit_to_beat(simplified, bpm, subdivision=subdivision)
    return filter_playable(simplified)


def metrics(notes):
    """Resumen útil para metadatos y para comparar variantes."""
    if not notes:
        return {
            "notes": 0,
            "onsets": 0,
            "min_pitch": None,
            "max_pitch": None,
            "median_fret": None,
            "max_fret": None,
            "high_frets": 0,
        }

    frets = []
    for pitch, _start, _end in notes:
        string_name, fret = pitch_to_string_fret(pitch, MAX_FRET)
        if string_name is not None:
            frets.append(fret)

    frets.sort()
    return {
        "notes": len(notes),
        "onsets": len({round(start, 2) for _, start, _ in notes}),
        "min_pitch": min(pitch for pitch, _, _ in notes),
        "max_pitch": max(pitch for pitch, _, _ in notes),
        "median_fret": frets[len(frets) // 2] if frets else None,
        "max_fret": max(frets) if frets else None,
        "high_frets": sum(fret >= 8 for fret in frets),
    }
