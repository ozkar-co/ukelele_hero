"""
Punto de entrada de Ukulele Hero.
Menú principal: juego, entrenador, detector de notas y calibración.
"""

import sys
from pathlib import Path

import pygame

# Los módulos del juego viven en src/ y se importan sin prefijo de paquete.
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from audio.profile_store import CalibrationProfileStore
from game.calibration_mode import CalibrationMode
from game.preview_mode import PreviewMode
from game.tablature_mode import TablatureGameMode
from game.trainer_mode import TrainerMode
from game.tuner_mode import TunerMode
from game.ui.theme import Theme
from music.tablature_manager import TablatureManager
from utils.config import BACKGROUND_COLOR, FPS, TEXT_COLOR, WINDOW_HEIGHT, WINDOW_WIDTH


class GameMenu:
    """Menú principal del juego"""

    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.manager = TablatureManager()
        self.profile = CalibrationProfileStore().load_latest()
        self.theme = Theme()

    def show_main_menu(self):
        """Muestra el menú principal"""
        running = True
        selected = 0
        options = [
            "Modo Juego",
            "Entrenador",
            "Escuchar Cancion",
            "Detector de Notas",
            "Calibrar Microfono",
            "Salir",
        ]

        while running:
            if not self.theme.draw_background(
                self.screen, "backgrounds/menu.png", dim=25
            ):
                self.screen.fill(BACKGROUND_COLOR)

            self.theme.draw_banner(
                self.screen, pygame.Rect(WINDOW_WIDTH // 2 - 330, 18, 660, 104)
            )
            self.theme.draw_text(
                self.screen,
                "UKULELE HERO",
                self.font_huge,
                (255, 100, 100),
                center=(WINDOW_WIDTH // 2, 58),
            )
            self.theme.draw_icon(
                self.screen, "icons/ukulele.png", (95, 100), 92
            )
            self.theme.draw_icon(
                self.screen, "icons/note.png", (930, 100), 44
            )
            self.theme.draw_icon(
                self.screen, "icons/sparkle.png", (872, 158), 26
            )

            for idx, option in enumerate(options):
                rect = pygame.Rect(
                    WINDOW_WIDTH // 2 - 230, 160 + idx * 74, 460, 62
                )
                self.theme.draw_button(
                    self.screen,
                    rect,
                    option,
                    self.font_large,
                    selected=(idx == selected),
                )

            if self.profile:
                thresholds = self.profile.get("thresholds", {})
                created = str(self.profile.get("created_at", "?"))[:19].replace("T", " ")
                profile_text = (
                    f"Perfil: {created} | "
                    f"vol {thresholds.get('min_volume', '?')} | "
                    f"conf {thresholds.get('min_confidence', '?')}"
                )
            else:
                profile_text = "Sin perfil de calibracion: valores por defecto"

            self.theme.draw_scrim(
                self.screen,
                pygame.Rect(WINDOW_WIDTH // 2 - 340, 606, 680, 34),
                alpha=170,
                color=(10, 25, 30),
            )
            self.theme.draw_text(
                self.screen,
                profile_text,
                self.font_small,
                (190, 200, 195),
                center=(WINDOW_WIDTH // 2, 623),
            )
            self.theme.draw_text(
                self.screen,
                "[FLECHAS]: Navegar | [ENTER]: Seleccionar",
                self.font_medium,
                (190, 200, 195),
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 45),
            )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(options)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(options)
                    elif event.key == pygame.K_RETURN:
                        return selected

            self.clock.tick(FPS)

        return None

    def show_tablature_select(self, title="Selecciona una Tablatura"):
        """Muestra selector de tablaturas"""
        tablatures = self.manager.get_saved_tablatures()

        if not tablatures:
            print("[ERROR] No hay tablaturas guardadas")
            input("Presiona ENTER para continuar...")
            return None

        running = True
        selected = 0
        scroll = 0
        visible_rows = 8

        while running:
            if selected < scroll:
                scroll = selected
            elif selected >= scroll + visible_rows:
                scroll = selected - visible_rows + 1

            if not self.theme.draw_background(
                self.screen, "backgrounds/menu.png", dim=60
            ):
                self.screen.fill(BACKGROUND_COLOR)

            self.theme.draw_panel(
                self.screen, pygame.Rect(60, 80, 904, 600), alpha=238
            )
            self.theme.draw_banner(
                self.screen, pygame.Rect(WINDOW_WIDTH // 2 - 330, 10, 660, 84)
            )
            self.theme.draw_text(
                self.screen,
                title,
                self.font_large,
                (255, 210, 120),
                center=(WINDOW_WIDTH // 2, 52),
            )
            self.theme.draw_icon(
                self.screen, "icons/note.png", (WINDOW_WIDTH - 110, 115), 38
            )

            for row, idx in enumerate(range(scroll, min(len(tablatures), scroll + visible_rows))):
                tab_name = tablatures[idx]
                row_y = 130 + row * 54
                is_selected = idx == selected

                if is_selected:
                    self.theme.draw_scrim(
                        self.screen,
                        pygame.Rect(90, row_y - 4, 844, 44),
                        alpha=150,
                        color=(70, 55, 25),
                    )
                    self.theme.draw_icon(
                        self.screen, "icons/sparkle.png", (116, row_y + 18), 22
                    )

                self.theme.draw_text(
                    self.screen,
                    tab_name[:72],
                    self.font_small,
                    (255, 220, 120) if is_selected else TEXT_COLOR,
                    topleft=(140, row_y + 6),
                )

            self.theme.draw_text(
                self.screen,
                f"{selected + 1}/{len(tablatures)}",
                self.font_small,
                (190, 200, 195),
                center=(WINDOW_WIDTH // 2, 645),
            )
            self.theme.draw_text(
                self.screen,
                "[FLECHAS]: Navegar | [ENTER]: Seleccionar | [ESC]: Atras",
                self.font_medium,
                (190, 200, 195),
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50),
            )

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        selected = (selected - 1) % len(tablatures)
                    elif event.key == pygame.K_DOWN:
                        selected = (selected + 1) % len(tablatures)
                    elif event.key == pygame.K_RETURN:
                        return tablatures[selected]
                    elif event.key == pygame.K_ESCAPE:
                        return None

            self.clock.tick(FPS)

        return None


def main():
    """Función principal del juego"""
    pygame.init()

    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ukulele Hero")

    menu = GameMenu(screen)

    while True:
        choice = menu.show_main_menu()

        if choice is None:
            break

        elif choice == 0:  # Modo Juego
            tab_name = menu.show_tablature_select()

            if tab_name:
                game_mode = TablatureGameMode(screen)

                if game_mode.load_tablature(tab_name):
                    game_mode.start()

        elif choice == 1:  # Entrenador
            tab_name = menu.show_tablature_select("Entrenador: elige una cancion")

            if tab_name:
                trainer = TrainerMode(screen)

                if trainer.load_tablature(tab_name):
                    trainer.start()

        elif choice == 2:  # Escuchar canción
            tab_name = menu.show_tablature_select("Escuchar: elige una cancion")

            if tab_name:
                preview = PreviewMode(screen)

                if preview.load_tablature(tab_name):
                    preview.start()

        elif choice == 3:  # Detector de Notas
            tuner = TunerMode(screen)
            tuner.start()

        elif choice == 4:  # Calibrar micrófono
            calibration = CalibrationMode(screen)
            calibration.start()
            menu.profile = CalibrationProfileStore().load_latest()

        elif choice == 5:  # Salir
            break

    pygame.quit()
    print("\n¡Gracias por jugar Ukulele Hero!")


if __name__ == "__main__":
    main()
