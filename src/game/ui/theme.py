"""
Tema visual compartido: fondos, paneles, botones e iconos pixel art.

Si falta una imagen, el juego sigue funcionando con los colores planos.
"""

import math
import sys
from pathlib import Path

import pygame

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.config import TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH

GOLD = (255, 210, 90)
DARK_TEAL = (14, 38, 43)


def _assets_root():
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent / "assets"
    return Path(__file__).parent.parent.parent.parent / "assets"


class Theme:
    """Carga y dibuja los assets visuales con caché."""

    def __init__(self):
        self.images_root = _assets_root() / "images"
        self._images = {}
        self._scaled = {}

    def image(self, relative_path):
        if relative_path in self._images:
            return self._images[relative_path]

        path = self.images_root / relative_path
        if not path.exists():
            self._images[relative_path] = None
            return None

        try:
            image = pygame.image.load(str(path)).convert_alpha()
        except pygame.error:
            image = None
        self._images[relative_path] = image
        return image

    def background(self, relative_path, dim=0):
        key = (relative_path, WINDOW_WIDTH, WINDOW_HEIGHT, dim)
        if key in self._scaled:
            return self._scaled[key]

        image = self.image(relative_path)
        if image is None:
            self._scaled[key] = None
            return None

        scaled = self._cover_scale(image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        if dim:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, dim))
            scaled = scaled.copy()
            scaled.blit(overlay, (0, 0))

        self._scaled[key] = scaled
        return scaled

    def draw_background(self, screen, relative_path, dim=0):
        background = self.background(relative_path, dim=dim)
        if background is None:
            return False
        screen.blit(background, (0, 0))
        return True

    def draw_icon(self, screen, relative_path, center, size):
        image = self.image(relative_path)
        if image is None:
            return False

        width, height = image.get_size()
        scale = size / max(width, height)
        scaled = pygame.transform.scale(
            image, (max(1, int(width * scale)), max(1, int(height * scale)))
        )
        rect = scaled.get_rect(center=center)
        screen.blit(scaled, rect)
        return True

    def draw_scrim(self, screen, rect, alpha=150, color=(0, 0, 0)):
        overlay = pygame.Surface(rect.size, pygame.SRCALPHA)
        overlay.fill((*color, alpha))
        screen.blit(overlay, rect.topleft)

    def draw_panel(self, screen, rect, alpha=235, image_name="ui/panel.png"):
        self.draw_scrim(screen, rect, alpha=alpha, color=DARK_TEAL)
        image = self.image(image_name)
        if image is not None:
            self._draw_nine_slice(screen, image, rect, draw_center=False)

    def draw_banner(self, screen, rect):
        self.draw_panel(screen, rect, alpha=245, image_name="ui/panel.png")

    def draw_button(self, screen, rect, label, font, selected=False):
        self.draw_scrim(screen, rect, alpha=245, color=DARK_TEAL)

        image = self.image("ui/button.png")
        if image is not None:
            self._draw_nine_slice(screen, image, rect, draw_center=False)
        else:
            pygame.draw.rect(screen, (70, 45, 30), rect, border_radius=6)
            pygame.draw.rect(screen, TEXT_COLOR, rect, 2, border_radius=6)

        if selected:
            pygame.draw.rect(screen, GOLD, rect, 3, border_radius=6)
            self.draw_icon(
                screen, "icons/note.png", (rect.x + 28, rect.centery), 26
            )

        self.draw_text(
            screen,
            label,
            font,
            GOLD if selected else TEXT_COLOR,
            center=rect.center,
            shadow=True,
        )

    def draw_text(
        self,
        screen,
        text,
        font,
        color=TEXT_COLOR,
        center=None,
        topleft=None,
        shadow=True,
    ):
        position = {"center": center} if center is not None else {"topleft": topleft}

        if shadow:
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_rect = shadow_surface.get_rect(**position)
            shadow_rect.move_ip(2, 2)
            screen.blit(shadow_surface, shadow_rect)

        surface = font.render(text, True, color)
        rect = surface.get_rect(**position)
        screen.blit(surface, rect)
        return rect

    def _cover_scale(self, image, size):
        target_width, target_height = size
        width, height = image.get_size()
        scale = max(target_width / width, target_height / height)
        new_size = (
            max(1, math.ceil(width * scale)),
            max(1, math.ceil(height * scale)),
        )
        scaled = pygame.transform.scale(image, new_size)
        offset_x = (new_size[0] - target_width) // 2
        offset_y = (new_size[1] - target_height) // 2
        return scaled.subsurface(
            (offset_x, offset_y, target_width, target_height)
        ).copy()

    def _draw_nine_slice(self, screen, image, rect, border=32, draw_center=True):
        image_width, image_height = image.get_size()
        source_border_x = min(border, image_width // 3)
        source_border_y = min(border, image_height // 3)
        dest_border_x = min(source_border_x, rect.width // 3)
        dest_border_y = min(source_border_y, rect.height // 3)

        source_columns = (
            (0, source_border_x, dest_border_x),
            (
                source_border_x,
                image_width - (2 * source_border_x),
                rect.width - (2 * dest_border_x),
            ),
            (
                image_width - source_border_x,
                source_border_x,
                dest_border_x,
            ),
        )
        source_rows = (
            (0, source_border_y, dest_border_y),
            (
                source_border_y,
                image_height - (2 * source_border_y),
                rect.height - (2 * dest_border_y),
            ),
            (
                image_height - source_border_y,
                source_border_y,
                dest_border_y,
            ),
        )

        dest_xs = (
            rect.x,
            rect.x + dest_border_x,
            rect.right - dest_border_x,
        )
        dest_ys = (
            rect.y,
            rect.y + dest_border_y,
            rect.bottom - dest_border_y,
        )

        for row_index, (source_y, source_h, dest_h) in enumerate(source_rows):
            for column_index, (source_x, source_w, dest_w) in enumerate(
                source_columns
            ):
                if source_w <= 0 or source_h <= 0 or dest_w <= 0 or dest_h <= 0:
                    continue
                if not draw_center and row_index == 1 and column_index == 1:
                    continue
                patch = image.subsurface(
                    (source_x, source_y, source_w, source_h)
                )
                scaled = pygame.transform.scale(patch, (dest_w, dest_h))
                screen.blit(
                    scaled,
                    (dest_xs[column_index], dest_ys[row_index]),
                )
