"""
Generador de tablaturas del juego (herramienta de depuración).

Genera archivos separados por variante, por ejemplo:
    cancion_track0_oct+1_normal.json
    cancion_track0_oct+1_easy.json

La variante easy es monofónica y se apoya en src/music/simplifier.py.
"""

import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from music.midi_loader import MIDILoader
from music.simplifier import filter_playable, metrics, simplify_easy
from music.tablature_manager import TablatureManager


def _choose_variants():
    while True:
        answer = input(
            "\nVariantes a generar: [ambas/normal/easy] (ambas): "
        ).strip().lower()
        if answer in ("", "ambas", "a"):
            return {"normal", "easy"}
        if answer in ("normal", "n"):
            return {"normal"}
        if answer in ("easy", "e"):
            return {"easy"}
        print("Opcion invalida")


def main():
    print("\n" + "=" * 60)
    print("[TABLATURE CREATOR] GENERADOR DE TABLATURAS")
    print("=" * 60 + "\n")

    loader = MIDILoader()
    manager = TablatureManager()

    midi_files = loader.get_midi_files()
    if not midi_files:
        print("No hay archivos MIDI en assets/midi/")
        return

    print("Archivos MIDI disponibles:")
    for index, filename in enumerate(midi_files, 1):
        print(f"  {index}. {filename}")

    while True:
        try:
            choice = int(input("\nSelecciona un archivo: ").strip())
            if 1 <= choice <= len(midi_files):
                midi_file = midi_files[choice - 1]
                break
        except ValueError:
            pass
        print("Opcion invalida")

    midi = loader.load_midi(midi_file)
    if not midi:
        return

    tracks_info = loader.get_track_info(midi)
    print("\nPistas disponibles:")
    for info in tracks_info:
        print(f"  {info['index']}. {info['name']} ({info['note_count']} notas)")

    while True:
        try:
            track = int(input("\nSelecciona pista: ").strip())
            if 0 <= track < len(tracks_info):
                break
        except ValueError:
            pass
        print("Opcion invalida")

    notes = loader.get_track_notes(midi, track)
    notes = loader.trim_silence(notes)
    if not notes:
        print("La pista no tiene notas")
        return

    tempo = midi.get_tempo_changes()[1][0] if midi.get_tempo_changes()[1].size else 120.0
    source_notes = len(notes)

    print("\nAjustando octava automaticamente...")
    notes, octaves = loader.adjust_to_ukulele_range(notes)
    if not notes:
        print("No quedaron notas tocables en el ukulele")
        return

    normal_metrics = metrics(notes)
    print(f"Octava elegida: {octaves:+d}")
    print(f"Notas tocables: {len(notes)}/{source_notes}")
    print(f"Traste mediano: {normal_metrics['median_fret']} | "
          f"maximo: {normal_metrics['max_fret']}")

    variants = _choose_variants()
    description = input("\nDescripcion (opcional): ").strip()

    metadata_base = {
        "description": description,
        "created_by": "MIDI Tool",
        "source_notes": source_notes,
        "octaves_transposed": octaves,
    }

    if "normal" in variants:
        filename = manager.save_tablature(
            midi_filename=midi_file,
            track_index=track,
            notes=notes,
            octaves_transposed=octaves,
            tempo=tempo,
            variant="normal",
            metadata={
                **metadata_base,
                "preset": "normal",
                "playable_metrics": normal_metrics,
            },
        )
        print(f"Variante normal: {filename}")

    if "easy" in variants:
        easy_notes = simplify_easy(notes, tempo, subdivision=1.0)
        easy_notes = filter_playable(easy_notes)
        if not easy_notes:
            print("La variante easy quedo vacia; no se guardo")
        else:
            easy_metrics = metrics(easy_notes)
            filename = manager.save_tablature(
                midi_filename=midi_file,
                track_index=track,
                notes=easy_notes,
                octaves_transposed=octaves,
                tempo=tempo,
                variant="easy",
                metadata={
                    **metadata_base,
                    "preset": "easy",
                    "playable_metrics": easy_metrics,
                    "processing": "skyline + remove_valleys + limit_to_beat",
                },
            )
            print(f"Variante easy: {filename}")


if __name__ == "__main__":
    main()
