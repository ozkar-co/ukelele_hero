"""
Tests del pipeline MIDI: octava automática, simplificación y variantes.
"""

import tempfile
import unittest
from pathlib import Path

from src.music.midi_loader import MIDILoader
from src.music.simplifier import (
    filter_playable,
    limit_to_beat,
    metrics,
    remove_valleys,
    simplify_easy,
    skyline,
)
from src.music.tablature_manager import TablatureManager


class TestAutoOctave(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.loader = MIDILoader(midi_folder=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_low_guitar_range_moves_up_one_octave(self):
        notes = [
            (40, 0.0, 0.5),
            (45, 0.5, 1.0),
            (52, 1.0, 1.5),
            (55, 1.5, 2.0),
            (59, 2.0, 2.5),
            (60, 2.5, 3.0),
            (64, 3.0, 3.5),
            (67, 3.5, 4.0),
            (69, 4.0, 4.5),
        ]

        adjusted, octaves = self.loader.adjust_to_ukulele_range(notes)

        self.assertEqual(octaves, 1)
        self.assertTrue(adjusted)
        self.assertTrue(all(60 <= pitch <= 88 for pitch, _, _ in adjusted))

    def test_in_range_melody_stays_put(self):
        notes = [
            (60, 0.0, 0.5),
            (62, 0.5, 1.0),
            (64, 1.0, 1.5),
            (65, 1.5, 2.0),
            (67, 2.0, 2.5),
        ]

        adjusted, octaves = self.loader.adjust_to_ukulele_range(notes)

        self.assertEqual(octaves, 0)
        self.assertEqual(adjusted, notes)


class TestSimplifier(unittest.TestCase):
    def test_skyline_takes_highest_per_onset(self):
        notes = [
            (60, 0.0, 0.5),
            (67, 0.0, 0.5),
            (64, 0.0, 0.5),
            (62, 0.5, 1.0),
        ]

        result = skyline(notes)

        self.assertEqual([pitch for pitch, _, _ in result], [67, 62])

    def test_remove_valleys_keeps_stepwise_notes(self):
        notes = [
            (72, 0.0, 0.5),
            (64, 0.5, 1.0),  # valle de 8 semitonos
            (72, 1.0, 1.5),
            (71, 1.5, 2.0),  # paso de 1 semitono
            (69, 2.0, 2.5),
        ]

        result = remove_valleys(notes, min_drop=4)

        self.assertEqual([pitch for pitch, _, _ in result], [72, 72, 71, 69])

    def test_limit_to_beat_keeps_highest_per_beat(self):
        notes = [
            (60, 0.0, 0.2),
            (67, 0.1, 0.2),
            (62, 0.5, 0.7),
            (64, 1.0, 1.2),
        ]

        result = limit_to_beat(notes, bpm=120, subdivision=1.0)

        self.assertEqual([pitch for pitch, _, _ in result], [67, 62, 64])

    def test_simplify_easy_is_monophonic_and_playable(self):
        notes = [
            (60, 0.0, 0.2),
            (67, 0.0, 0.2),
            (62, 0.25, 0.4),
            (64, 0.5, 0.7),
            (65, 0.75, 0.9),
            (67, 1.0, 1.2),
        ]

        result = simplify_easy(notes, bpm=120, subdivision=1.0)

        self.assertTrue(result)
        self.assertEqual(len(result), len({round(start, 2) for _, start, _ in result}))
        self.assertEqual(result, filter_playable(result))
        self.assertTrue(metrics(result)["notes"] > 0)


class TestVariantFiles(unittest.TestCase):
    def test_variant_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            manager = TablatureManager(tablature_folder=tmp)
            notes = [(60, 0.0, 0.5), (62, 0.5, 1.0)]

            normal = manager.save_tablature(
                "song", 0, notes, octaves_transposed=1, tempo=120, variant="normal"
            )
            easy = manager.save_tablature(
                "song", 0, notes, octaves_transposed=1, tempo=120, variant="easy"
            )

            self.assertTrue(normal.endswith("_normal.json"))
            self.assertTrue(easy.endswith("_easy.json"))
            self.assertTrue((Path(tmp) / normal).exists())
            self.assertTrue((Path(tmp) / easy).exists())


if __name__ == "__main__":
    unittest.main()
