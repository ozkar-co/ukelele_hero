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
            self.screen.fill(BACKGROUND_COLOR)

            title = self.font_huge.render("UKULELE HERO", True, (255, 100, 100))
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.blit(title, title_rect)

            for idx, option in enumerate(options):
                color = (255, 255, 100) if idx == selected else TEXT_COLOR
                text = self.font_large.render(option, True, color)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 180 + idx * 70))
                self.screen.blit(text, text_rect)

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
            profile_surface = self.font_small.render(
                profile_text, True, (150, 150, 150)
            )
            self.screen.blit(
                profile_surface,
                profile_surface.get_rect(center=(WINDOW_WIDTH // 2, 590)),
            )

            instr = self.font_medium.render(
                "[FLECHAS]: Navegar | [ENTER]: Seleccionar", True, (150, 150, 150)
            )
            instr_rect = instr.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(instr, instr_rect)

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

        while running:
            self.screen.fill(BACKGROUND_COLOR)

            title_surface = self.font_large.render(title, True, TEXT_COLOR)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, 40))
            self.screen.blit(title_surface, title_rect)

            for idx, tab_name in enumerate(tablatures):
                color = (255, 255, 100) if idx == selected else TEXT_COLOR
                text = self.font_medium.render(f"  {tab_name}", True, color)
                self.screen.blit(text, (50, 120 + idx * 50))

            instr = self.font_medium.render(
                "[FLECHAS]: Navegar | [ENTER]: Seleccionar | [ESC]: Atrás",
                True,
                (150, 150, 150),
            )
            instr_rect = instr.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(instr, instr_rect)

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
