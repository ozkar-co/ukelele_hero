"""
Componente reutilizable que dibuja las cuerdas y las notas de una tablatura.

Lo usan el modo juego, el entrenador y el modo de escucha para que el
aspecto visual y los estilos vivan en un solo lugar.
"""

import sys
from pathlib import Path

import pygame

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from game.ui.styles import (
    HIT_ZONE_COLOR,
    HIT_ZONE_LINE_COLOR,
    HIT_ZONE_WIDTH,
    HIT_ZONE_X,
    LANE_BOTTOM_MARGIN,
    LANE_TOP,
    NOTE_HEIGHT,
    NOTE_OUTLINE_DIVISOR,
    NOTE_SPEED_PIXELS_PER_SECOND,
    NOTE_TEXT_COLOR,
    NOTE_WIDTH,
    STRING_COLORS,
    STRING_ORDER,
)
from utils.config import TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH


class TablatureView:
    """Dibuja las 4 cuerdas, la zona de golpeo y las notas que se desplazan."""

    STRINGS = STRING_ORDER
    STRING_COLORS = STRING_COLORS
    HIT_ZONE_X = HIT_ZONE_X
    HIT_ZONE_WIDTH = HIT_ZONE_WIDTH
    NOTE_WIDTH = NOTE_WIDTH
    NOTE_HEIGHT = NOTE_HEIGHT
    NOTE_SPEED_PIXELS_PER_SECOND = NOTE_SPEED_PIXELS_PER_SECOND

    def __init__(self, screen):
        self.screen = screen
        self.font_string = pygame.font.Font(None, 72)
        self.font_fret = pygame.font.Font(None, 40)
        self.string_y_positions = self._calculate_layout()

    def _calculate_layout(self):
        spacing = (
            WINDOW_HEIGHT - LANE_TOP - LANE_BOTTOM_MARGIN
        ) // len(STRING_ORDER)
        return {
            string_name: LANE_TOP + (index * spacing)
            for index, string_name in enumerate(STRING_ORDER)
        }

    def note_x(self, start_time, current_time):
        """Posición horizontal de una nota en el tiempo actual."""
        return HIT_ZONE_X + (
            start_time - current_time
        ) * NOTE_SPEED_PIXELS_PER_SECOND

    def draw(self, notes, current_time):
        """Dibuja cuerdas, zona de golpeo y notas."""
        self.draw_strings()
        self.draw_hit_zone()
        self.draw_notes(notes, current_time)

    def draw_strings(self):
        for string_name, y in self.string_y_positions.items():
            color = STRING_COLORS[string_name]

            label = self.font_string.render(string_name, True, color)
            self.screen.blit(label, (20, y - 20))

            pygame.draw.line(
                self.screen,
                color,
                (HIT_ZONE_X + HIT_ZONE_WIDTH, y),
                (WINDOW_WIDTH, y),
                2,
            )

    def draw_hit_zone(self):
        pygame.draw.rect(
            self.screen,
            HIT_ZONE_COLOR,
            (HIT_ZONE_X, 80, HIT_ZONE_WIDTH, WINDOW_HEIGHT - 160),
        )
        pygame.draw.line(
            self.screen,
            HIT_ZONE_LINE_COLOR,
            (HIT_ZONE_X, 80),
            (HIT_ZONE_X, WINDOW_HEIGHT - 80),
            3,
        )

    def draw_notes(self, notes, current_time):
        for note in notes:
            self.draw_note(note, self.note_x(note["start_time"], current_time))

    def draw_note(self, note, x):
        if x < -NOTE_WIDTH or x > WINDOW_WIDTH:
            return

        y = self.string_y_positions[note["string"]]
        color = STRING_COLORS[note["string"]]

        pygame.draw.rect(
            self.screen,
            color,
            (x, y - NOTE_HEIGHT // 2, NOTE_WIDTH, NOTE_HEIGHT),
        )
        pygame.draw.rect(
            self.screen,
            tuple(c // NOTE_OUTLINE_DIVISOR for c in color),
            (x, y - NOTE_HEIGHT // 2, NOTE_WIDTH, NOTE_HEIGHT),
            2,
        )

        fret_text = self.font_fret.render(str(note["fret"]), True, NOTE_TEXT_COLOR)
        fret_rect = fret_text.get_rect(center=(x + NOTE_WIDTH // 2, y))
        self.screen.blit(fret_text, fret_rect)

    def draw_target(self, string_name):
        """Marca la nota actual del entrenador en la zona de golpeo."""
        y = self.string_y_positions[string_name]
        pygame.draw.circle(
            self.screen,
            TEXT_COLOR,
            (HIT_ZONE_X + NOTE_WIDTH // 2, y),
            34,
            2,
        )
