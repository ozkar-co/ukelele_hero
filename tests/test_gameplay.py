"""
Tests de la validación de notas del modo juego.
"""

import unittest

from src.game.tablature_mode import TablatureGameMode


def make_game(notes, current_time):
    game = TablatureGameMode.__new__(TablatureGameMode)
    game.active_notes = list(notes)
    game.current_time = current_time
    game._last_hit_pitch = None
    game._gap_since_hit = True
    game.hits = []
    game._on_note_hit = lambda note, abs_error, signed_error: game.hits.append(
        (note, abs_error, signed_error)
    )
    return game


def make_note(note, pitch, start):
    return {
        "note": note,
        "pitch": pitch,
        "start_time": start,
        "end_time": start + 0.5,
        "fret": 0,
        "string": "C",
    }


class TestGameHitDetection(unittest.TestCase):
    def test_matching_note_in_window_is_hit(self):
        note = make_note("C4", 60, 1.0)
        game = make_game([note], current_time=1.05)

        game._try_hit({"note": "C4"})

        self.assertEqual(len(game.hits), 1)
        self.assertEqual(game.active_notes, [])
        self.assertAlmostEqual(game.hits[0][1], 0.05)

    def test_wrong_note_is_not_hit(self):
        note = make_note("C4", 60, 1.0)
        game = make_game([note], current_time=1.0)

        game._try_hit({"note": "D4"})

        self.assertEqual(game.hits, [])
        self.assertEqual(game.active_notes, [note])

    def test_note_outside_window_is_not_hit(self):
        note = make_note("C4", 60, 1.0)
        game = make_game([note], current_time=1.3)

        game._try_hit({"note": "C4"})

        self.assertEqual(game.hits, [])

    def test_same_pitch_requires_a_gap(self):
        first = make_note("C4", 60, 1.0)
        second = make_note("C4", 60, 1.25)
        game = make_game([first, second], current_time=1.0)

        game._try_hit({"note": "C4"})
        game.current_time = 1.25
        game._try_hit({"note": "C4"})

        self.assertEqual(len(game.hits), 1)

        game._gap_since_hit = True
        game._try_hit({"note": "C4"})
        self.assertEqual(len(game.hits), 2)

    def test_game_end_without_notes_does_not_divide_by_zero(self):
        game = TablatureGameMode.__new__(TablatureGameMode)
        game.hits = 0
        game.misses = 0
        game.score = 0
        game.max_combo = 0
        game.is_running = True

        game._on_game_end()

        self.assertFalse(game.is_running)


if __name__ == "__main__":
    unittest.main()
