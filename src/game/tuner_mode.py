"""
Modo Afinador - Etapa 1 del juego Ukulele Master
Muestra la nota detectada y su estado de afinación
"""

import pygame
import sys
from ..audio.note_detector import NoteDetector
from ..utils.config import *
from ..utils.helpers import format_frequency, format_cents


class TunerMode:
    """Modo afinador para detectar y mostrar notas en tiempo real"""
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Detector de notas
        self.note_detector = NoteDetector()
        
        # Fuentes
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, FONT_XLARGE)
        self.font_medium = pygame.font.Font(None, FONT_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SMALL)
        
        # Estado del afinador
        self.is_running = False
        self.current_detection = None
        
        # Elementos visuales
        self.needle_angle = 0  # Ángulo de la aguja del afinador
        self.volume_bars = []
        
    def start(self):
        """Inicia el modo afinador"""
        print("Iniciando modo afinador...")
        
        # Iniciar detector de notas
        if not self.note_detector.start_detection():
            print("Error: No se pudo iniciar la detección de audio")
            return False
        
        self.is_running = True
        self.run()
        return True
    
    def stop(self):
        """Detiene el modo afinador"""
        self.is_running = False
        self.note_detector.stop_detection()
        print("Modo afinador detenido")
    
    def run(self):
        """Bucle principal del modo afinador"""
        while self.is_running:
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop()
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.stop()
                        return
                    elif event.key == pygame.K_SPACE:
                        self._toggle_detection()
            
            # Actualizar detector de notas
            self.current_detection = self.note_detector.update()
            
            # Actualizar visualización
            self._update_visuals()
            
            # Dibujar pantalla
            self._draw()
            
            # Control de FPS
            self.clock.tick(FPS)
    
    def _toggle_detection(self):
        """Alternar detección de audio"""
        if self.note_detector.is_detecting:
            self.note_detector.stop_detection()
        else:
            self.note_detector.start_detection()
    
    def _update_visuals(self):
        """Actualiza elementos visuales basados en la detección actual"""
        if self.current_detection:
            # Actualizar ángulo de aguja basado en desviación
            deviation = self.current_detection['deviation']
            # Normalizar desviación a rango -50 a +50 cents para visualización
            max_deviation = 50
            normalized_deviation = max(-max_deviation, min(max_deviation, deviation))
            # Convertir a ángulo (-45° a +45°)
            self.needle_angle = (normalized_deviation / max_deviation) * 45
        else:
            # Volver aguja al centro
            self.needle_angle *= 0.9  # Suavizado
    
    def _draw(self):
        """Dibuja la interfaz del afinador"""
        # Fondo
        self.screen.fill(BACKGROUND_COLOR)
        
        # Título
        title_text = self.font_large.render("🎵 AFINADOR UKULELE 🎵", True, HIGHLIGHT_COLOR)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # Estado de detección
        status_color = SUCCESS_COLOR if self.note_detector.is_detecting else ERROR_COLOR
        status_text = "🎤 DETECTANDO" if self.note_detector.is_detecting else "🎤 PAUSADO"
        status_surface = self.font_medium.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(center=(WINDOW_WIDTH // 2, 120))
        self.screen.blit(status_surface, status_rect)
        
        if self.current_detection:
            self._draw_note_detection()
        else:
            self._draw_no_signal()
        
        # Instrucciones
        self._draw_instructions()
        
        # Referencias de cuerdas del ukulele
        self._draw_ukulele_reference()
        
        pygame.display.flip()
    
    def _draw_note_detection(self):
        """Dibuja la información de la nota detectada"""
        detection = self.current_detection
        
        # Nota principal (grande en el centro)
        note_text = self.font_huge.render(detection['note'], True, TEXT_COLOR)
        note_rect = note_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(note_text, note_rect)
        
        # Frecuencia
        freq_text = self.font_medium.render(
            format_frequency(detection['frequency']), True, TEXT_COLOR
        )
        freq_rect = freq_text.get_rect(center=(WINDOW_WIDTH // 2, 300))
        self.screen.blit(freq_text, freq_rect)
        
        # Estado de afinación
        tuning_status = detection['tuning_status']
        if tuning_status == 'perfect':
            status_color = SUCCESS_COLOR
            status_text = "¡AFINADO!"
        elif tuning_status == 'sharp':
            status_color = ORANGE
            status_text = "MUY AGUDO"
        else:  # flat
            status_color = CYAN
            status_text = "MUY GRAVE"
        
        tuning_surface = self.font_medium.render(status_text, True, status_color)
        tuning_rect = tuning_surface.get_rect(center=(WINDOW_WIDTH // 2, 340))
        self.screen.blit(tuning_surface, tuning_rect)
        
        # Desviación en cents
        cents_text = format_cents(detection['deviation'])
        cents_surface = self.font_medium.render(cents_text, True, TEXT_COLOR)
        cents_rect = cents_surface.get_rect(center=(WINDOW_WIDTH // 2, 370))
        self.screen.blit(cents_surface, cents_rect)
        
        # Medidor visual de afinación
        self._draw_tuning_meter(detection['deviation'])
        
        # Barra de confianza
        self._draw_confidence_bar(detection['confidence'])
        
        # Barra de volumen
        self._draw_volume_bar(detection['volume'])
    
    def _draw_no_signal(self):
        """Dibuja mensaje cuando no hay señal"""
        no_signal_text = self.font_large.render("Toca una nota...", True, TEXT_COLOR)
        no_signal_rect = no_signal_text.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(no_signal_text, no_signal_rect)
        
        # Mostrar barra de volumen aunque no haya nota
        volume = self.note_detector.microphone.get_volume_level()
        self._draw_volume_bar(volume)
    
    def _draw_tuning_meter(self, deviation):
        """Dibuja el medidor de afinación tipo aguja"""
        center_x = WINDOW_WIDTH // 2
        center_y = 450
        radius = 80
        
        # Dibujar arco del medidor
        pygame.draw.arc(self.screen, TEXT_COLOR, 
                       (center_x - radius, center_y - radius, 
                        radius * 2, radius * 2), 
                       3.14, 0, 3)
        
        # Marcas del medidor
        for angle in [-45, -22.5, 0, 22.5, 45]:
            rad = (angle * 3.14159) / 180
            start_x = center_x + (radius - 15) * math.cos(rad)
            start_y = center_y - (radius - 15) * math.sin(rad)
            end_x = center_x + radius * math.cos(rad)
            end_y = center_y - radius * math.sin(rad)
            pygame.draw.line(self.screen, TEXT_COLOR, (start_x, start_y), (end_x, end_y), 2)
        
        # Dibujar aguja
        needle_rad = (self.needle_angle * 3.14159) / 180
        needle_x = center_x + (radius - 10) * math.cos(needle_rad)
        needle_y = center_y - (radius - 10) * math.sin(needle_rad)
        
        needle_color = SUCCESS_COLOR if abs(deviation) <= 10 else ERROR_COLOR
        pygame.draw.line(self.screen, needle_color, 
                        (center_x, center_y), (needle_x, needle_y), 4)
        
        # Centro de la aguja
        pygame.draw.circle(self.screen, needle_color, (center_x, center_y), 5)
    
    def _draw_confidence_bar(self, confidence):
        """Dibuja barra de confianza de la detección"""
        bar_width = 200
        bar_height = 10
        bar_x = WINDOW_WIDTH // 2 - bar_width // 2
        bar_y = 520
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de confianza
        confidence_width = int(bar_width * confidence)
        confidence_color = SUCCESS_COLOR if confidence > 0.7 else ORANGE if confidence > 0.4 else ERROR_COLOR
        pygame.draw.rect(self.screen, confidence_color, (bar_x, bar_y, confidence_width, bar_height))
        
        # Etiqueta
        label_text = self.font_small.render(f"Confianza: {confidence:.1%}", True, TEXT_COLOR)
        label_rect = label_text.get_rect(center=(WINDOW_WIDTH // 2, bar_y + bar_height + 15))
        self.screen.blit(label_text, label_rect)
    
    def _draw_volume_bar(self, volume):
        """Dibuja barra de volumen del micrófono"""
        bar_width = 200
        bar_height = 8
        bar_x = WINDOW_WIDTH // 2 - bar_width // 2
        bar_y = 560
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height))
        
        # Barra de volumen
        volume_width = int(bar_width * min(volume * 5, 1.0))  # Amplificar para visualización
        pygame.draw.rect(self.screen, GREEN, (bar_x, bar_y, volume_width, bar_height))
        
        # Etiqueta
        label_text = self.font_small.render("Volumen", True, TEXT_COLOR)
        label_rect = label_text.get_rect(center=(WINDOW_WIDTH // 2, bar_y + bar_height + 15))
        self.screen.blit(label_text, label_rect)
    
    def _draw_instructions(self):
        """Dibuja las instrucciones"""
        instructions = [
            "ESPACIO: Pausar/Reanudar detección",
            "ESC: Volver al menú principal"
        ]
        
        y_offset = 620
        for instruction in instructions:
            text = self.font_small.render(instruction, True, TEXT_COLOR)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset))
            self.screen.blit(text, text_rect)
            y_offset += 25
    
    def _draw_ukulele_reference(self):
        """Dibuja referencia de las cuerdas del ukulele"""
        # Cuerdas del ukulele
        strings_info = [
            ("4ª cuerda", "G4", "392.0 Hz"),
            ("3ª cuerda", "C4", "261.6 Hz"),
            ("2ª cuerda", "E4", "329.6 Hz"),
            ("1ª cuerda", "A4", "440.0 Hz")
        ]
        
        x_start = 50
        y_start = 200
        
        # Título
        title_text = self.font_medium.render("Referencia Ukulele:", True, HIGHLIGHT_COLOR)
        self.screen.blit(title_text, (x_start, y_start - 30))
        
        for i, (string_name, note, freq) in enumerate(strings_info):
            y_pos = y_start + i * 30
            
            # Nombre de la cuerda
            name_text = self.font_small.render(string_name, True, TEXT_COLOR)
            self.screen.blit(name_text, (x_start, y_pos))
            
            # Nota
            note_text = self.font_small.render(note, True, HIGHLIGHT_COLOR)
            self.screen.blit(note_text, (x_start + 80, y_pos))
            
            # Frecuencia
            freq_text = self.font_small.render(freq, True, TEXT_COLOR)
            self.screen.blit(freq_text, (x_start + 120, y_pos))


# Necesitamos importar math para los cálculos trigonométricos
import math