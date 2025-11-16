#!/usr/bin/env python3
"""
Ukulele Master - Main entry point
Un juego tipo Guitar Hero para ukulele
"""

import pygame
import sys
from src.game.ui.screens import MainMenu
from src.utils.config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS, WINDOW_TITLE


def main():
    """Función principal del juego"""
    # Inicializar pygame
    pygame.init()
    pygame.mixer.init()
    
    # Crear ventana del juego
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption(WINDOW_TITLE)
    
    # Reloj para controlar FPS
    clock = pygame.time.Clock()
    
    # Crear menú principal
    main_menu = MainMenu(screen)
    
    # Bucle principal del juego
    running = True
    while running:
        # Manejar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                main_menu.handle_event(event)
        
        # Actualizar
        main_menu.update()
        
        # Dibujar
        screen.fill((0, 0, 0))  # Fondo negro
        main_menu.draw(screen)
        pygame.display.flip()
        
        # Controlar FPS
        clock.tick(FPS)
    
    # Limpiar y salir
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()