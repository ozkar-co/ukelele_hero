"""
Cálculo de umbrales de detección a partir de una calibración.

La lógica es pura para poder probarla sin micrófono ni interfaz: recibe
muestras de silencio y de notas, y devuelve el perfil serializable.
"""

from datetime import datetime

import numpy as np

from utils.config import MIN_VOLUME_THRESHOLD, NOTE_TOLERANCE_CENTS


def _clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def summarize_noise(noise_samples):
    """Resume las muestras RMS tomadas en silencio."""
    samples = np.asarray(noise_samples, dtype=float)
    if samples.size == 0:
        return {"floor_rms": 0.0, "peak_rms": 0.0, "samples": 0}

    return {
        "floor_rms": float(np.percentile(samples, 50)),
        "peak_rms": float(np.percentile(samples, 90)),
        "samples": int(samples.size),
    }


def summarize_note(string_name, fret, note_name, expected_frequency, samples):
    """
    Resume las muestras válidas de una nota.

    Cada muestra debe tener frequency, confidence, volume y deviation.
    """
    if not samples:
        return {
            "string": string_name,
            "fret": fret,
            "note": note_name,
            "expected_frequency": round(expected_frequency, 2),
            "mean_frequency": None,
            "mean_cents_offset": None,
            "mean_confidence": None,
            "mean_volume": None,
            "samples": 0,
        }

    return {
        "string": string_name,
        "fret": fret,
        "note": note_name,
        "expected_frequency": round(expected_frequency, 2),
        "mean_frequency": round(
            float(np.mean([s["frequency"] for s in samples])), 2
        ),
        "mean_cents_offset": round(
            float(np.mean([s["deviation"] for s in samples])), 2
        ),
        "mean_confidence": round(
            float(np.mean([s["confidence"] for s in samples])), 3
        ),
        "mean_volume": round(float(np.mean([s["volume"] for s in samples])), 4),
        "samples": len(samples),
    }


def compute_thresholds(noise_samples, note_summaries):
    """
    Calcula umbrales de detección adaptados al silencio y a las notas medidas.

    - min_volume queda por encima del ruido de sala, pero por debajo del
      volumen de las notas más suaves.
    - min_confidence se deriva de la confianza real observada.
    - note_tolerance_cents se amplía si el instrumento quedó desviado.
    """
    noise = summarize_noise(noise_samples)
    valid_notes = [n for n in note_summaries if n.get("samples")]

    min_volume = noise["peak_rms"] * 2.5 + 0.002

    note_volumes = [n["mean_volume"] for n in valid_notes]
    if note_volumes:
        quiet_note_volume = float(np.percentile(note_volumes, 20))
        min_volume = min(min_volume, quiet_note_volume * 0.5)
    else:
        min_volume = max(min_volume, MIN_VOLUME_THRESHOLD)

    min_volume = _clamp(min_volume, 0.003, 0.08)

    confidences = [n["mean_confidence"] for n in valid_notes]
    if confidences:
        mean_confidence = float(np.mean(confidences))
        min_confidence = _clamp(mean_confidence * 0.6, 0.2, 0.55)
    else:
        mean_confidence = None
        min_confidence = 0.3

    cents_offsets = [abs(n["mean_cents_offset"]) for n in valid_notes]
    if cents_offsets:
        mean_abs_cents = float(np.mean(cents_offsets))
        note_tolerance = _clamp(8 + (2 * mean_abs_cents), 10, 25)
    else:
        mean_abs_cents = None
        note_tolerance = NOTE_TOLERANCE_CENTS

    return {
        "min_volume": round(min_volume, 4),
        "min_confidence": round(min_confidence, 3),
        "note_tolerance_cents": round(note_tolerance, 1),
        "history_size": 5,
        "mean_confidence": (
            round(mean_confidence, 3) if mean_confidence is not None else None
        ),
        "mean_abs_cents_offset": (
            round(mean_abs_cents, 2) if mean_abs_cents is not None else None
        ),
    }


def build_profile(noise_samples, note_summaries, total_notes, device=None):
    """Construye el perfil completo que se guarda en disco."""
    noise = summarize_noise(noise_samples)
    thresholds = compute_thresholds(noise_samples, note_summaries)
    valid_notes = [n for n in note_summaries if n.get("samples")]

    return {
        "version": 1,
        "app": "ukelele_hero",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "device": device or {},
        "noise": noise,
        "thresholds": thresholds,
        "notes": note_summaries,
        "summary": {
            "notes_total": int(total_notes),
            "notes_completed": len(valid_notes),
            "notes_skipped": int(total_notes) - len(valid_notes),
            "reliable": len(valid_notes) >= 3,
        },
    }
