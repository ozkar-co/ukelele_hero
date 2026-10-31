"""
Tests del cálculo de umbrales y del almacenamiento de perfiles.
"""

import tempfile
import unittest
from pathlib import Path

from src.audio.calibration import (
    build_profile,
    compute_thresholds,
    summarize_note,
    summarize_noise,
)
from src.audio.note_detector import NoteDetector
from src.audio.profile_store import CalibrationProfileStore


def make_note(string_name, fret, note, samples):
    return summarize_note(string_name, fret, note, 261.63, samples)


def sample(frequency=261.6, confidence=0.8, volume=0.02, deviation=2.0):
    return {
        "frequency": frequency,
        "confidence": confidence,
        "volume": volume,
        "deviation": deviation,
    }


class TestCalibrationThresholds(unittest.TestCase):
    def test_noise_summary(self):
        summary = summarize_noise([0.001, 0.002, 0.003, 0.004])
        self.assertAlmostEqual(summary["floor_rms"], 0.0025, places=4)
        self.assertEqual(summary["samples"], 4)

    def test_thresholds_above_noise(self):
        noise = [0.002] * 100
        notes = [
            make_note("C", 0, "C4", [sample(volume=0.02)] * 20),
            make_note("E", 0, "E4", [sample(volume=0.025)] * 20),
            make_note("A", 0, "A4", [sample(volume=0.03)] * 20),
        ]
        thresholds = compute_thresholds(noise, notes)

        self.assertGreater(thresholds["min_volume"], 0.002)
        self.assertGreaterEqual(thresholds["min_volume"], 0.003)
        self.assertLessEqual(thresholds["min_volume"], 0.08)
        self.assertGreater(thresholds["min_confidence"], 0.3)
        self.assertLess(thresholds["min_confidence"], 0.55)

    def test_no_valid_notes_uses_defaults(self):
        thresholds = compute_thresholds([0.001] * 10, [])
        self.assertEqual(thresholds["min_confidence"], 0.3)
        self.assertEqual(thresholds["note_tolerance_cents"], 10.0)

    def test_summarize_note(self):
        summary = make_note(
            "C",
            2,
            "D4",
            [sample(frequency=293.0, confidence=0.7)] * 4,
        )
        self.assertEqual(summary["samples"], 4)
        self.assertEqual(summary["note"], "D4")
        self.assertAlmostEqual(summary["mean_frequency"], 293.0, places=2)
        self.assertAlmostEqual(summary["mean_confidence"], 0.7, places=3)

    def test_profile_requires_three_notes(self):
        profile = build_profile(
            [0.001] * 10,
            [make_note("C", 0, "C4", [sample()] * 5)],
            total_notes=10,
        )
        self.assertFalse(profile["summary"]["reliable"])
        self.assertEqual(profile["summary"]["notes_completed"], 1)
        self.assertEqual(profile["summary"]["notes_skipped"], 9)


class TestDetectorProfile(unittest.TestCase):
    def test_profile_thresholds_are_applied(self):
        detector = NoteDetector(
            profile={
                "thresholds": {
                    "min_volume": 0.02,
                    "min_confidence": 0.45,
                    "note_tolerance_cents": 15,
                    "history_size": 3,
                }
            }
        )

        self.assertEqual(detector.min_volume_threshold, 0.02)
        self.assertEqual(detector.min_confidence, 0.45)
        self.assertEqual(detector.note_tolerance_cents, 15)
        self.assertEqual(detector.history_size, 3)

    def test_empty_profile_uses_defaults(self):
        detector = NoteDetector(profile={})
        self.assertEqual(detector.history_size, 5)
        self.assertGreater(detector.min_volume_threshold, 0)


class TestProfileStore(unittest.TestCase):
    def test_save_and_load_latest(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CalibrationProfileStore(folder=Path(tmp))
            first = store.save({"thresholds": {"min_volume": 0.01}, "tag": "first"})
            second = store.save({"thresholds": {"min_volume": 0.02}, "tag": "second"})

            self.assertTrue(first.exists())
            self.assertTrue(second.exists())
            self.assertEqual(len(store.list_profiles()), 2)

            latest = store.load_latest()
            self.assertEqual(latest["tag"], "second")
            self.assertIn("created_at", latest)

    def test_empty_store(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = CalibrationProfileStore(folder=Path(tmp))
            self.assertIsNone(store.load_latest())


if __name__ == "__main__":
    unittest.main()
