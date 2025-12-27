"""
Pantallas principales del juego Ukulele Master
"""

import pygame
import sys
from pathlib import Path

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.config import *


class MainMenu:
    """Menú principal del juego"""
    
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.Font(None, FONT_XLARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        
        # Opciones del menú
        self.menu_options = [
            "1. Detector de Notas (Etapa 1)",
            "2. Simon Musical (Etapa 2)", 
            "3. Juego Completo (Etapa 3)",
            "4. Configuración",
            "5. Salir"
        ]
        
        self.selected_option = 0
        
    def handle_event(self, event):
        """Manejar eventos del menú"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self.select_option()
                
    def select_option(self):
        """Procesar la opción seleccionada"""
        if self.selected_option == 0:
            print("Iniciando Detector de Notas...")
            from ..tuner_mode import TunerMode
            detector = TunerMode(self.screen)
            detector.start()
        elif self.selected_option == 1:
            print("Iniciando Simon Musical...")
            # TODO: Implementar modo Simon
        elif self.selected_option == 2:
            print("Iniciando Juego Completo...")
            # TODO: Implementar juego completo
        elif self.selected_option == 3:
            print("Abriendo Configuración...")
            # TODO: Implementar configuración
        elif self.selected_option == 4:
            pygame.event.post(pygame.event.Event(pygame.QUIT))
            
    def update(self):
        """Actualizar el menú"""
        pass
        
    def draw(self, screen):
        """Dibujar el menú"""
        # Título del juego
        title_text = self.font_large.render("UKULELE MASTER", True, HIGHLIGHT_COLOR)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Subtítulo
        subtitle_text = self.font_medium.render("Guitar Hero para Ukulele", True, TEXT_COLOR)
        subtitle_rect = subtitle_text.get_rect(center=(WINDOW_WIDTH // 2, 200))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Opciones del menú
        start_y = 300
        for i, option in enumerate(self.menu_options):
            color = HIGHLIGHT_COLOR if i == self.selected_option else TEXT_COLOR
            option_text = self.font_medium.render(option, True, color)
            option_rect = option_text.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 50))
            screen.blit(option_text, option_rect)
            
        # Instrucciones
        instructions = [
            "Usa las flechas para navegar",
            "Presiona ENTER para seleccionar",
            "ESC para salir"
        ]
        
        instruction_y = 600
        for instruction in instructions:
            instruction_text = self.font_medium.render(instruction, True, TEXT_COLOR)
            instruction_rect = instruction_text.get_rect(center=(WINDOW_WIDTH // 2, instruction_y))
            screen.blit(instruction_text, instruction_rect)
            instruction_y += 30