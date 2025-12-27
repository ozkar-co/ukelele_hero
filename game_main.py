"""
Programa principal - Ukulele Hero
Modo juego con tablaturas configuradas
"""

import pygame
import sys
from pathlib import Path

# Agregar src al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from game.tablature_mode import TablatureGameMode
from game.tuner_mode import TunerMode
from utils.config import *
from music.tablature_manager import TablatureManager


class GameMenu:
    """Menú principal del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        
        self.manager = TablatureManager()
    
    def show_main_menu(self):
        """Muestra el menú principal"""
        running = True
        selected = 0
        options = ["Modo Juego", "Detector de Notas", "Salir"]
        
        while running:
            self.screen.fill(BACKGROUND_COLOR)
            
            # Título
            title = self.font_huge.render("UKULELE HERO", True, (255, 100, 100))
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.blit(title, title_rect)
            
            # Opciones
            for idx, option in enumerate(options):
                color = (255, 255, 100) if idx == selected else TEXT_COLOR
                text = self.font_large.render(option, True, color)
                text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 200 + idx * 80))
                self.screen.blit(text, text_rect)
            
            # Instrucciones
            instr = self.font_medium.render("[FLECHAS]: Navegar | [ENTER]: Seleccionar", True, (150, 150, 150))
            instr_rect = instr.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(instr, instr_rect)
            
            pygame.display.flip()
            
            # Manejo de eventos
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
    
    def show_tablature_select(self):
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
            
            # Título
            title = self.font_large.render("Selecciona una Tablatura", True, TEXT_COLOR)
            title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 40))
            self.screen.blit(title, title_rect)
            
            # Lista de tablaturas
            for idx, tab_name in enumerate(tablatures):
                color = (255, 255, 100) if idx == selected else TEXT_COLOR
                text = self.font_medium.render(f"  {tab_name}", True, color)
                self.screen.blit(text, (50, 120 + idx * 50))
            
            # Instrucciones
            instr = self.font_medium.render("[FLECHAS]: Navegar | [ENTER]: Seleccionar | [ESC]: Atrás", 
                                           True, (150, 150, 150))
            instr_rect = instr.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
            self.screen.blit(instr, instr_rect)
            
            pygame.display.flip()
            
            # Manejo de eventos
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
    """Función principal"""
    # Inicializar pygame
    pygame.init()
    
    # Crear ventana
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Ukulele Hero - Modo Tablaturas")
    
    # Menú principal
    menu = GameMenu(screen)
    
    while True:
        choice = menu.show_main_menu()
        
        if choice is None:
            break
        
        elif choice == 0:  # Modo Juego
            # Seleccionar tablatura
            tab_name = menu.show_tablature_select()
            
            if tab_name:
                # Crear modo juego
                game_mode = TablatureGameMode(screen)
                
                # Cargar tablatura
                if game_mode.load_tablature(tab_name):
                    # Iniciar juego
                    game_mode.start()
        
        elif choice == 1:  # Detector de Notas
            tuner = TunerMode(screen)
            tuner.start()
        
        elif choice == 2:  # Salir
            break
    
    pygame.quit()
    print("\n¡Gracias por jugar Ukulele Hero!")


if __name__ == "__main__":
    main()
