"""
Modo Calibración - mide el silencio y varias notas para ajustar los
umbrales de detección al micrófono y al ruido de la sala.

Cada calibración se guarda como un perfil nuevo en assets/calibration/.
NoteDetector carga automáticamente el perfil más reciente al iniciar.
"""

import sys
import time
from pathlib import Path

import numpy as np
import pygame

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from audio.calibration import build_profile, summarize_note
from audio.frequency_analyzer import FrequencyAnalyzer
from audio.microphone import MicrophoneCapture
from audio.profile_store import CalibrationProfileStore
from game.ui.theme import Theme
from music.ukelele import pitch_to_note_name, string_fret_to_pitch
from utils.config import (
    BACKGROUND_COLOR,
    CYAN,
    ERROR_COLOR,
    FONT_MEDIUM,
    FONT_SMALL,
    FONT_XLARGE,
    FPS,
    HIGHLIGHT_COLOR,
    NOTE_FREQUENCIES,
    ORANGE,
    SUCCESS_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from utils.helpers import format_cents, format_frequency, frequency_to_note


# Posiciones a calibrar: cuerdas al aire y trastes representativos.
CALIBRATION_POSITIONS = [
    ("A", 0),
    ("E", 0),
    ("C", 0),
    ("G", 0),
    ("C", 2),
    ("C", 5),
    ("A", 2),
    ("A", 3),
    ("A", 5),
    ("A", 7),
]

SILENCE_SECONDS = 3.0
NOTE_SETTLE_SECONDS = 0.8
NOTE_MIN_SAMPLES = 10
MIN_VALID_NOTES = 3


class CalibrationMode:
    """Calibra el micrófono en dos fases: silencio y notas guiadas."""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.microphone = MicrophoneCapture()
        self.analyzer = FrequencyAnalyzer()
        self.store = CalibrationProfileStore()
        self.theme = Theme()

        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, FONT_XLARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        self.font_tiny = pygame.font.Font(None, 20)

        self.targets = self._build_targets()
        self.is_running = False
        self.step = 0  # 0 = silencio, 1..N = notas, N+1 = resultados

        self.noise_samples = []
        self.completed_notes = []
        self.current_samples = []
        self.step_started = 0.0
        self.note_started_at = None

        self.current_volume = 0.0
        self.current_frequency = 0.0
        self.current_confidence = 0.0
        self.current_note = None
        self.current_deviation = 0.0

        self.profile = None
        self.saved_path = None
        self.results_saved = False

    @staticmethod
    def _build_targets():
        targets = []
        for string_name, fret in CALIBRATION_POSITIONS:
            pitch = string_fret_to_pitch(string_name, fret)
            note = pitch_to_note_name(pitch)
            targets.append(
                {
                    "string": string_name,
                    "fret": fret,
                    "pitch": pitch,
                    "note": note,
                    "frequency": NOTE_FREQUENCIES[note],
                }
            )
        return targets

    def start(self):
        """Inicia la calibración completa."""
        print("Iniciando calibración de micrófono...")

        if not self.microphone.start_capture():
            print("Error: no se pudo iniciar la captura de audio")
            return False

        self._reset_all()
        self.is_running = True
        try:
            self.run()
        finally:
            self.microphone.stop_capture()

        return True

    def _reset_all(self):
        self.step = 0
        self.noise_samples = []
        self.completed_notes = []
        self.current_samples = []
        self.step_started = time.monotonic()
        self.note_started_at = None
        self.profile = None
        self.saved_path = None
        self.results_saved = False

    def run(self):
        """Bucle principal."""
        while self.is_running:
            self._handle_events()
            self._update()
            self._draw()
            self.clock.tick(FPS)

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                elif event.key == pygame.K_r:
                    self._reset_all()

                elif event.key == pygame.K_RETURN:
                    if self.step > len(self.targets):
                        self.is_running = False
                    elif 1 <= self.step <= len(self.targets):
                        self._finish_note(skipped=True)

                elif event.key == pygame.K_SPACE:
                    if 1 <= self.step <= len(self.targets):
                        self.current_samples = []
                        self.note_started_at = None
                        self.step_started = time.monotonic()

    def _capture(self):
        audio_data = self.microphone.get_audio_data()
        volume = (
            float(np.sqrt(np.mean(audio_data ** 2))) if len(audio_data) else 0.0
        )
        analysis = self.analyzer.analyze_frequency(audio_data)
        note, deviation = frequency_to_note(analysis["frequency"])

        self.current_volume = volume
        self.current_frequency = analysis["frequency"]
        self.current_confidence = analysis["confidence"]
        self.current_note = note
        self.current_deviation = deviation
        return volume, analysis, note, deviation

    def _update(self):
        now = time.monotonic()
        volume, analysis, note, deviation = self._capture()

        if self.step == 0:
            self.noise_samples.append(volume)
            if now - self.step_started >= SILENCE_SECONDS:
                self.step = 1
                self.step_started = now
                self.note_started_at = None
            return

        if not (1 <= self.step <= len(self.targets)):
            return

        target = self.targets[self.step - 1]
        if note == target["note"] and volume >= 0.0005:
            if self.note_started_at is None:
                self.note_started_at = now
            self.current_samples.append(
                {
                    "frequency": analysis["frequency"],
                    "confidence": analysis["confidence"],
                    "volume": volume,
                    "deviation": deviation,
                }
            )

        if self.note_started_at is None:
            return

        held_for = now - self.note_started_at
        if held_for >= NOTE_SETTLE_SECONDS and len(self.current_samples) >= NOTE_MIN_SAMPLES:
            self._finish_note(skipped=False)

    def _finish_note(self, skipped):
        target = self.targets[self.step - 1]
        summary = summarize_note(
            target["string"],
            target["fret"],
            target["note"],
            target["frequency"],
            [] if skipped else self.current_samples,
        )
        self.completed_notes.append(summary)

        self.current_samples = []
        self.note_started_at = None
        self.step += 1
        self.step_started = time.monotonic()

        if self.step > len(self.targets):
            self._finish_calibration()

    def _finish_calibration(self):
        if self.results_saved:
            return

        self.profile = build_profile(
            self.noise_samples,
            self.completed_notes,
            len(self.targets),
            device=self._device_info(),
        )
        if self.profile["summary"]["reliable"]:
            self.saved_path = self.store.save(self.profile)
            print(f"Perfil de calibración guardado: {self.saved_path}")
        else:
            print("Calibración incompleta: no se guardó el perfil")

        self.results_saved = True

    def _device_info(self):
        index = self.microphone.device_index
        name = "predeterminado"
        try:
            for device in self.microphone.get_input_devices():
                if device["index"] == index:
                    name = device["name"]
                    break
        except Exception:
            pass
        return {"index": index, "name": name}

    def _draw(self):
        if not self.theme.draw_background(
            self.screen, "backgrounds/menu.png", dim=95
        ):
            self.screen.fill(BACKGROUND_COLOR)

        self.theme.draw_panel(
            self.screen, pygame.Rect(40, 75, 944, 670), alpha=235
        )
        self.theme.draw_text(
            self.screen,
            "CALIBRACION DE MICROFONO",
            self.font_large,
            HIGHLIGHT_COLOR,
            center=(WINDOW_WIDTH // 2, 50),
        )
        self.theme.draw_icon(
            self.screen, "icons/ukulele.png", (100, 50), 48
        )

        if self.step == 0:
            self._draw_silence()
        elif self.step <= len(self.targets):
            self._draw_note()
        else:
            self._draw_results()

        pygame.display.flip()

    def _draw_silence(self):
        now = time.monotonic()
        remaining = max(0.0, SILENCE_SECONDS - (now - self.step_started))

        self._draw_step_label("Paso 1: ruido de sala")
        text = self.font_huge.render("SILENCIO", True, TEXT_COLOR)
        self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, 230)))

        hint = self.font_medium.render(
            "No toques el ukelele durante la medicion", True, TEXT_COLOR
        )
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 300)))

        countdown = self.font_huge.render(
            f"{remaining:.1f}s", True, HIGHLIGHT_COLOR
        )
        self.screen.blit(countdown, countdown.get_rect(center=(WINDOW_WIDTH // 2, 400)))

        self._draw_bar(
            WINDOW_WIDTH // 2 - 200,
            480,
            400,
            18,
            min(self.current_volume * 20, 1.0),
            CYAN,
            f"Ruido actual: {self.current_volume:.4f} RMS",
        )

        self._draw_instructions(["ESC: cancelar", "R: reiniciar"])

    def _draw_note(self):
        target = self.targets[self.step - 1]
        self._draw_step_label(
            f"Paso {self.step + 1}/{len(self.targets) + 1}: "
            f"cuerda {target['string']} - traste {target['fret']}"
        )

        note_text = self.font_huge.render(target["note"], True, HIGHLIGHT_COLOR)
        self.screen.blit(note_text, note_text.get_rect(center=(WINDOW_WIDTH // 2, 190)))

        position = self.font_large.render(
            f"Cuerda {target['string']}  |  traste {target['fret']}",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(position, position.get_rect(center=(WINDOW_WIDTH // 2, 255)))

        expected = self.font_medium.render(
            f"Esperado: {format_frequency(target['frequency'])}", True, TEXT_COLOR
        )
        self.screen.blit(expected, expected.get_rect(center=(WINDOW_WIDTH // 2, 295)))

        hint = self.font_small.render(
            "Toca la nota y mantenla hasta completar la barra", True, (180, 180, 180)
        )
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, 330)))

        if self.current_note:
            detected_color = (
                SUCCESS_COLOR if self.current_note == target["note"] else ORANGE
            )
            detected = self.font_medium.render(
                f"Ahora: {self.current_note}  "
                f"{format_frequency(self.current_frequency)}  "
                f"({self.current_confidence:.1%})",
                True,
                detected_color,
            )
        else:
            detected = self.font_medium.render(
                "Ahora: sin nota estable", True, (150, 150, 150)
            )
        self.screen.blit(detected, detected.get_rect(center=(WINDOW_WIDTH // 2, 390)))

        if self.note_started_at is None:
            progress = 0.0
        else:
            progress = min(
                1.0, (time.monotonic() - self.note_started_at) / NOTE_SETTLE_SECONDS
            )
        self._draw_bar(
            WINDOW_WIDTH // 2 - 200,
            440,
            400,
            20,
            progress,
            SUCCESS_COLOR,
            f"Muestras validas: {len(self.current_samples)}/{NOTE_MIN_SAMPLES}",
        )

        self._draw_bar(
            WINDOW_WIDTH // 2 - 200,
            500,
            400,
            14,
            min(self.current_volume * 10, 1.0),
            CYAN,
            f"Volumen: {self.current_volume:.4f} RMS",
        )

        if self.current_note:
            cents = format_cents(self.current_deviation)
            self._draw_bar(
                WINDOW_WIDTH // 2 - 200,
                555,
                400,
                14,
                min(self.current_confidence, 1.0),
                ORANGE,
                f"Confianza: {self.current_confidence:.1%}  |  desvio: {cents}",
            )

        self._draw_instructions(
            [
                "ESPACIO: repetir nota",
                "ENTER: saltar nota",
                "R: reiniciar calibracion",
                "ESC: cancelar",
            ]
        )

    def _draw_results(self):
        if self.saved_path:
            headline = self.font_large.render("Perfil guardado", True, SUCCESS_COLOR)
            detail = self.font_small.render(self.saved_path.name, True, TEXT_COLOR)
            reliability = "Perfil valido"
        else:
            headline = self.font_large.render(
                "Calibracion incompleta", True, ERROR_COLOR
            )
            detail = self.font_small.render(
                f"Se completaron menos de {MIN_VALID_NOTES} notas; no se guardo perfil",
                True,
                TEXT_COLOR,
            )
            reliability = "Repite con R"

        self.screen.blit(
            headline, headline.get_rect(center=(WINDOW_WIDTH // 2, 120))
        )
        self.screen.blit(detail, detail.get_rect(center=(WINDOW_WIDTH // 2, 155)))

        if self.profile:
            thresholds = self.profile["thresholds"]
            noise = self.profile["noise"]
            lines = [
                f"Umbral de volumen: {thresholds['min_volume']:.4f} RMS",
                f"Umbral de confianza: {thresholds['min_confidence']:.1%}",
                f"Tolerancia de afinacion: {thresholds['note_tolerance_cents']:.0f} cents",
                f"Ruido de sala: {noise['floor_rms']:.4f} RMS "
                f"(pico {noise['peak_rms']:.4f})",
                f"Notas completadas: {self.profile['summary']['notes_completed']}"
                f"/{self.profile['summary']['notes_total']}",
            ]
            y = 210
            for line in lines:
                surface = self.font_medium.render(line, True, TEXT_COLOR)
                self.screen.blit(surface, (150, y))
                y += 34

            y += 10
            header = self.font_small.render(
                "Resumen por nota:", True, HIGHLIGHT_COLOR
            )
            self.screen.blit(header, (150, y))
            y += 28

            for note in self.profile["notes"]:
                if note["samples"]:
                    text = (
                        f"{note['string']}{note['fret']} {note['note']}: "
                        f"conf {note['mean_confidence']:.2f}  "
                        f"desvio {format_cents(note['mean_cents_offset'])}"
                    )
                    color = TEXT_COLOR
                else:
                    text = f"{note['string']}{note['fret']} {note['note']}: omitida"
                    color = (150, 150, 150)
                surface = self.font_tiny.render(text, True, color)
                self.screen.blit(surface, (170, y))
                y += 22

        self._draw_instructions(
            [reliability, "ENTER o ESC: volver al menu", "R: repetir calibracion"]
        )

    def _draw_step_label(self, text):
        surface = self.font_medium.render(text, True, TEXT_COLOR)
        self.screen.blit(
            surface, surface.get_rect(center=(WINDOW_WIDTH // 2, 105))
        )

    def _draw_bar(self, x, y, width, height, value, color, label):
        pygame.draw.rect(self.screen, (60, 60, 60), (x, y, width, height))
        pygame.draw.rect(
            self.screen, color, (x, y, int(width * max(0.0, min(value, 1.0))), height)
        )
        pygame.draw.rect(self.screen, TEXT_COLOR, (x, y, width, height), 1)
        text = self.font_tiny.render(label, True, TEXT_COLOR)
        self.screen.blit(text, (x, y + height + 8))

    def _draw_instructions(self, lines):
        y = WINDOW_HEIGHT - 45 - (len(lines) - 1) * 22
        for line in lines:
            text = self.font_small.render(line, True, (160, 160, 160))
            self.screen.blit(
                text, text.get_rect(center=(WINDOW_WIDTH // 2, y))
            )
            y += 22
