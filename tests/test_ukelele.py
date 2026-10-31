"""
Tests de la afinación GCEA y del mapeo cuerda/traste.
"""

import unittest

from src.music.ukelele import (
    OPEN_STRING_PITCHES,
    pitch_to_note_name,
    pitch_to_string_fret,
    string_fret_to_pitch,
)


class TestUkuleleMapping(unittest.TestCase):
    def test_open_strings(self):
        for string_name, pitch in OPEN_STRING_PITCHES.items():
            self.assertEqual(string_fret_to_pitch(string_name, 0), pitch)
            self.assertEqual(pitch_to_string_fret(pitch), (string_name, 0))

    def test_fretted_notes(self):
        self.assertEqual(string_fret_to_pitch("C", 2), 62)
        self.assertEqual(pitch_to_string_fret(62), ("C", 2))
        self.assertEqual(pitch_to_string_fret(72), ("A", 3))
        self.assertEqual(pitch_to_string_fret(76), ("A", 7))

    def test_prefers_lowest_fret(self):
        # F4 se puede tocar en E1 o C5; debe elegir E1.
        self.assertEqual(pitch_to_string_fret(65), ("E", 1))

    def test_out_of_range(self):
        self.assertEqual(pitch_to_string_fret(20), (None, None))
        self.assertIsNone(string_fret_to_pitch("C", 99))
        self.assertIsNone(string_fret_to_pitch("X", 0))

    def test_note_names(self):
        self.assertEqual(pitch_to_note_name(60), "C4")
        self.assertEqual(pitch_to_note_name(69), "A4")
        self.assertEqual(pitch_to_note_name(72), "C5")


if __name__ == "__main__":
    unittest.main()
