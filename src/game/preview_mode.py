"""
Modo Escucha - reproduce la tablatura con tonos sintetizados mientras
las notas se desplazan por las cuerdas.

Sirve para comprobar si una variante normal/easy sigue sonando reconocible
sin exportar un MIDI a otra herramienta.
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

from game.ui.styles import STRING_ORDER
from game.ui.tablature_view import TablatureView
from game.ui.theme import Theme
from music.tablature_manager import TablatureManager
from music.ukelele import pitch_to_string_fret
from utils.config import (
    BACKGROUND_COLOR,
    FPS,
    HIGHLIGHT_COLOR,
    SUCCESS_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)

LEAD_IN_SECONDS = 1.0
NOTE_DURATION_SECONDS = 0.35


class PreviewMode:
    """Reproduce una tablatura y muestra las notas en movimiento."""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.manager = TablatureManager()
        self.view = TablatureView(screen)
        self.theme = Theme()

        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.notes = []
        self.source = ""
        self.variant = ""
        self.tempo = 120.0
        self.duration = 0.0

        self.is_running = False
        self.paused = False
        self.finished = False
        self.current_time = 0.0
        self.start_ticks = 0.0
        self.next_note_index = 0

        self.audio_enabled = False
        self.sound_cache = {}

    def load_tablature(self, tablature_name):
        tab_data = self.manager.load_tablature(tablature_name)
        if not tab_data:
            return False

        notes = []
        for raw_note in tab_data.get("notes", []):
            string_name, fret = pitch_to_string_fret(raw_note["pitch"])
            if string_name is None:
                continue
            notes.append(
                {
                    "pitch": raw_note["pitch"],
                    "note": raw_note["note_name"],
                    "string": string_name,
                    "fret": fret,
                    "start_time": raw_note["start_time"] + LEAD_IN_SECONDS,
                    "end_time": raw_note["end_time"] + LEAD_IN_SECONDS,
                }
            )

        notes.sort(
            key=lambda note: (
                note["start_time"],
                STRING_ORDER.index(note["string"]),
            )
        )
        if not notes:
            return False

        self.notes = notes
        self.source = tab_data["source"]["midi_file"]
        self.variant = tab_data.get("metadata", {}).get("preset", "normal")
        self.tempo = tab_data["configuration"]["tempo"]
        self.duration = notes[-1]["end_time"] + 0.5
        return True

    def start(self):
        if not self.notes:
            print("[PREVIEW] No hay notas cargadas")
            return False

        self._init_audio()
        self._reset()
        self.is_running = True

        try:
            self.run()
        finally:
            self._stop_audio()

        return True

    def stop(self):
        self.is_running = False
        self._stop_audio()

    def _stop_audio(self):
        if pygame.mixer.get_init() is not None:
            pygame.mixer.stop()

    def run(self):
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)

    def _init_audio(self):
        init = pygame.mixer.get_init()
        if init is None:
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
                init = pygame.mixer.get_init()
            except pygame.error:
                init = None

        self.audio_enabled = init is not None
        if self.audio_enabled:
            pygame.mixer.set_num_channels(32)

    def _reset(self):
        self.paused = False
        self.finished = False
        self.current_time = 0.0
        self.start_ticks = time.monotonic()
        self.next_note_index = 0
        self._stop_audio()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                elif event.key == pygame.K_SPACE and not self.finished:
                    self.paused = not self.paused
                    self._stop_audio()
                    if not self.paused:
                        self.start_ticks = time.monotonic() - self.current_time

                elif event.key == pygame.K_r:
                    self._reset()

                elif event.key == pygame.K_RETURN and self.finished:
                    self._reset()

    def _update(self):
        if self.paused or self.finished:
            return

        self.current_time = time.monotonic() - self.start_ticks

        while (
            self.next_note_index < len(self.notes)
            and self.notes[self.next_note_index]["start_time"] <= self.current_time
        ):
            self._play_note(self.notes[self.next_note_index])
            self.next_note_index += 1

        if self.current_time > self.duration:
            self.finished = True
            self._stop_audio()

    def _play_note(self, note):
        if not self.audio_enabled:
            return

        sound = self.sound_cache.get(note["pitch"])
        if sound is None:
            sound = self._make_sound(note["pitch"])
            if sound is None:
                return
            self.sound_cache[note["pitch"]] = sound

        sound.play()

    def _make_sound(self, pitch):
        try:
            init = pygame.mixer.get_init()
            if init is None:
                return None
            sample_rate, _sample_format, channels = init

            frequency = 440.0 * (2.0 ** ((pitch - 69) / 12.0))
            times = np.linspace(
                0, NOTE_DURATION_SECONDS, int(sample_rate * NOTE_DURATION_SECONDS), False
            )
            envelope = np.minimum(1.0, times / 0.01) * np.exp(-4.0 * times)
            wave = (
                0.22 * np.sin(2 * np.pi * frequency * times)
                + 0.06 * np.sin(4 * np.pi * frequency * times)
            ) * envelope

            samples = (wave * 32767).astype(np.int16)
            if channels == 2:
                samples = np.column_stack([samples, samples])

            return pygame.sndarray.make_sound(samples)
        except (pygame.error, ValueError):
            self.audio_enabled = False
            return None

    def _render(self):
        if not self.theme.draw_background(
            self.screen, "backgrounds/game.png", dim=110
        ):
            self.screen.fill(BACKGROUND_COLOR)

        header = (
            f"ESCUCHA | {self.source} | {self.variant} | "
            f"{self.tempo:.0f} BPM | {self.current_time:.1f}s"
        )
        self.theme.draw_scrim(
            self.screen, pygame.Rect(0, 0, WINDOW_WIDTH, 46), alpha=145
        )
        self.theme.draw_text(
            self.screen, header, self.font_medium, TEXT_COLOR, topleft=(20, 10)
        )

        self.view.draw(self.notes, self.current_time)

        self.theme.draw_scrim(
            self.screen,
            pygame.Rect(0, WINDOW_HEIGHT - 90, WINDOW_WIDTH, 90),
            alpha=145,
        )

        if self.finished:
            self.theme.draw_panel(
                self.screen,
                pygame.Rect(WINDOW_WIDTH // 2 - 240, WINDOW_HEIGHT // 2 - 90, 480, 180),
                alpha=235,
            )
            message = self.font_large.render("FIN", True, SUCCESS_COLOR)
            self.screen.blit(
                message, message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            )
            hint = self.font_medium.render(
                "ENTER/R: repetir | ESC: salir", True, TEXT_COLOR
            )
            self.screen.blit(
                hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 50))
            )
        elif self.paused:
            self.theme.draw_panel(
                self.screen,
                pygame.Rect(WINDOW_WIDTH // 2 - 200, WINDOW_HEIGHT // 2 - 70, 400, 140),
                alpha=235,
            )
            message = self.font_large.render("PAUSA", True, HIGHLIGHT_COLOR)
            self.screen.blit(
                message, message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            )
        else:
            status = "Audio: ON" if self.audio_enabled else "Audio: OFF"
            status_surface = self.font_small.render(status, True, (170, 170, 170))
            self.screen.blit(status_surface, (20, WINDOW_HEIGHT - 30))

        instructions = "ESPACIO: pausa | R: reiniciar | ESC: salir"
        inst_surface = self.font_small.render(instructions, True, (150, 150, 150))
        self.screen.blit(
            inst_surface,
            inst_surface.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 55)
            ),
        )

        pygame.display.flip()
