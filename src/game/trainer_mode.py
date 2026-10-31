"""
Modo Entrenador - muestra una tablatura y espera a que el jugador toque
la nota indicada antes de avanzar.

Reutiliza el renderizado del modo juego, pero el tiempo queda congelado
en la nota actual: no hay puntuación por tiempo, solo práctica guiada.
"""

import sys
import time
from pathlib import Path

import pygame

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from game.tablature_mode import TablatureGameMode
from music.ukelele import pitch_to_string_fret
from utils.config import (
    HIGHLIGHT_COLOR,
    ORANGE,
    SUCCESS_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from utils.helpers import format_frequency


class TrainerMode(TablatureGameMode):
    """Práctica nota a nota: la canción avanza cuando suena la nota pedida."""

    def __init__(self, screen):
        super().__init__(screen)

        self.notes = []
        self.current_index = 0
        self.completed_notes = 0
        self.skipped_notes = 0
        self.current_detection = None
        self.status_message = ""
        self.match_streak = 0
        self.gap_seen = True
        self.last_accepted_pitch = None
        self.accept_cooldown_until = 0.0
        self.finished = False

    def load_tablature(self, tablature_name):
        """Carga la tablatura y calcula cuerda/traste reales de cada nota."""
        tab_data = self.tab_manager.load_tablature(tablature_name)
        if not tab_data:
            return False

        notes = []
        for raw_note in tab_data.get("notes", []):
            pitch = raw_note["pitch"]
            string_name, fret = pitch_to_string_fret(pitch)
            if string_name is None:
                print(f"[TRAINER] Nota fuera del ukulele: {raw_note['note_name']}")
                continue

            notes.append(
                {
                    "fret": fret,
                    "pitch": pitch,
                    "note": raw_note["note_name"],
                    "string": string_name,
                    "start_time": raw_note["start_time"],
                    "end_time": raw_note["end_time"],
                    "duration": raw_note["end_time"] - raw_note["start_time"],
                }
            )

        notes.sort(
            key=lambda note: (
                note["start_time"],
                self.STRINGS.index(note["string"]),
            )
        )

        self.notes = notes
        self.active_notes = [dict(note) for note in notes]
        self.upcoming_notes = list(self.notes)
        self.current_tablature = {
            "source": tab_data["source"]["midi_file"],
            "track": tab_data["source"]["track_index"],
            "tempo": tab_data["configuration"]["tempo"],
            "octaves_transposed": tab_data["configuration"]["octaves_transposed"],
            "statistics": tab_data.get("statistics", {}),
            "total_notes": len(notes),
        }
        self.current_index = 0
        self.finished = False
        self._sync_time()

        print(f"[TRAINER] Tablatura cargada: {len(notes)} notas")
        return bool(notes)

    def start(self):
        """Inicia el entrenador."""
        if not self.notes:
            print("[TRAINER] No hay notas cargadas")
            return False

        if not self.note_detector.start_detection():
            print("[TRAINER] No se pudo iniciar la deteccion de audio")

        self.is_running = True
        self._reset_progress()
        try:
            self.run()
        finally:
            self.stop()
        return True

    def _reset_progress(self):
        self.current_index = 0
        self.completed_notes = 0
        self.skipped_notes = 0
        self.current_detection = None
        self.status_message = ""
        self.match_streak = 0
        self.gap_seen = True
        self.last_accepted_pitch = None
        self.accept_cooldown_until = 0.0
        self.finished = False
        self._sync_time()

    def _current_note(self):
        if 0 <= self.current_index < len(self.notes):
            return self.notes[self.current_index]
        return None

    def _sync_time(self):
        """Congela el tiempo en la nota actual."""
        current = self._current_note()
        self.current_time = current["start_time"] if current else 0.0

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

                elif event.key == pygame.K_r:
                    self._reset_progress()

                elif event.key == pygame.K_SPACE and not self.finished:
                    self._skip_current()

                elif event.key == pygame.K_RETURN and self.finished:
                    self._reset_progress()

    def _skip_current(self):
        if self.finished:
            return
        self.skipped_notes += 1
        self._advance()

    def _accept_current(self, now):
        note = self._current_note()
        if note is None:
            return

        self.completed_notes += 1
        self.last_accepted_pitch = note["pitch"]
        self.gap_seen = False
        self.match_streak = 0
        self.accept_cooldown_until = now + 0.3
        self.status_message = "Bien"
        self._advance()

    def _advance(self):
        self.current_index += 1
        self.match_streak = 0
        self.current_detection = None

        if self.current_index >= len(self.notes):
            self.finished = True
            self.current_time = self.notes[-1]["end_time"]
        else:
            self._sync_time()

    def _update(self):
        if self.finished:
            return

        self._sync_time()
        now = time.monotonic()
        detection = self.note_detector.update()
        self.current_detection = detection

        if detection is None:
            self.gap_seen = True
            self.match_streak = 0
            return

        target = self._current_note()
        if target is None:
            return

        if detection["note"] != target["note"]:
            self.match_streak = 0
            self.status_message = (
                f"Detectado {detection['note']}; se pide {target['note']}"
            )
            return

        if now < self.accept_cooldown_until:
            return

        if target["pitch"] == self.last_accepted_pitch and not self.gap_seen:
            self.status_message = "Repite la nota"
            return

        self.match_streak += 1
        if self.match_streak >= 2:
            self._accept_current(now)

    def _render_header(self):
        if not self.current_tablature:
            return

        total = len(self.notes)
        position = min(self.current_index + 1, total) if total else 0
        header = (
            f"ENTRENADOR | {self.current_tablature['source']} | "
            f"{position}/{total} | {self.current_tablature['tempo']} BPM"
        )
        surface = self.font_medium.render(header, True, TEXT_COLOR)
        self.screen.blit(surface, (20, 10))

    def _render_hud(self):
        target = self._current_note()

        if self.finished:
            message = self.font_large.render(
                "Cancion completada", True, SUCCESS_COLOR
            )
            self.screen.blit(
                message, message.get_rect(center=(WINDOW_WIDTH // 2, 250))
            )

            stats = self.font_medium.render(
                f"Tocadas: {self.completed_notes} | "
                f"Saltadas: {self.skipped_notes}",
                True,
                TEXT_COLOR,
            )
            self.screen.blit(stats, stats.get_rect(center=(WINDOW_WIDTH // 2, 320)))

            instructions = "ENTER: repetir | R: reiniciar | ESC: salir"
            inst = self.font_small.render(instructions, True, (150, 150, 150))
            self.screen.blit(
                inst, inst.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 40))
            )
            return

        if target:
            prompt = self.font_large.render(
                f"Toca {target['note']}", True, HIGHLIGHT_COLOR
            )
            self.screen.blit(
                prompt, prompt.get_rect(center=(WINDOW_WIDTH // 2, 595))
            )

            position = self.font_medium.render(
                f"Cuerda {target['string']} | traste {target['fret']}",
                True,
                TEXT_COLOR,
            )
            self.screen.blit(
                position, position.get_rect(center=(WINDOW_WIDTH // 2, 642))
            )

            if self.current_detection:
                detected = self.current_detection
                matches = detected["note"] == target["note"]
                status = (
                    f"Escucho: {detected['note']} "
                    f"{format_frequency(detected['frequency'])}"
                )
                color = SUCCESS_COLOR if matches else ORANGE
            else:
                status = self.status_message or "Esperando nota..."
                color = (170, 170, 170)

            status_surface = self.font_medium.render(status, True, color)
            self.screen.blit(
                status_surface,
                status_surface.get_rect(center=(WINDOW_WIDTH // 2, 675)),
            )

            self.view.draw_target(target["string"])

        progress = self.font_small.render(
            f"Nota {self.current_index + 1}/{len(self.notes)} | "
            f"Tocadas: {self.completed_notes} | Saltadas: {self.skipped_notes}",
            True,
            TEXT_COLOR,
        )
        self.screen.blit(progress, (20, WINDOW_HEIGHT - 70))

        instructions = "ESPACIO: saltar nota | R: reiniciar | ESC: salir"
        inst = self.font_small.render(instructions, True, (150, 150, 150))
        self.screen.blit(inst, (20, WINDOW_HEIGHT - 35))
