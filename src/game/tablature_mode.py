"""
Modo Juego de Tablaturas - Vista estilo Guitar Hero horizontal
Las notas se desplazan de derecha a izquierda según el tempo
"""

import pygame
import sys
from pathlib import Path

# Agregar src al path para imports absolutos
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from audio.note_detector import NoteDetector
from utils.config import *
from utils.helpers import format_frequency
from music.tablature_manager import TablatureManager


class TablatureGameMode:
    """Modo juego con tablaturas - notas desplazándose horizontalmente"""
    
    # Configuración de layout
    STRINGS = ['G', 'C', 'E', 'A']
    STRING_COLORS = {
        'G': (255, 100, 100),  # Rojo
        'C': (100, 255, 100),  # Verde
        'E': (100, 100, 255),  # Azul
        'A': (255, 255, 100),  # Amarillo
    }
    
    HIT_ZONE_X = 150  # X donde las notas deben tocarse (izquierda)
    HIT_ZONE_WIDTH = 40  # Ancho de la zona de golpeo
    HIT_ZONE_MARGIN = 100  # Margen de error en pixels
    
    NOTE_WIDTH = 30  # Ancho de las notas
    NOTE_SPEED_PIXELS_PER_SECOND = 400  # Velocidad en pixels/segundo
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Gestor de tablaturas
        self.tab_manager = TablatureManager()
        
        # Estado del juego
        self.current_tablature = None
        self.is_running = False
        self.game_paused = False
        self.current_time = 0.0  # Tiempo en segundos
        self.start_time = 0.0
        
        # Notas activas (en pantalla)
        self.active_notes = []  # Lista de notas que se están mostrando
        self.upcoming_notes = []  # Cola de notas por aparecer
        self.note_index = 0
        
        # Scoring
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0  # Notas tocadas correctamente
        self.misses = 0
        
        # Detector de notas (para validar si se tocó la nota correcta)
        self.note_detector = NoteDetector()
        
        # Fuentes
        self.font_huge = pygame.font.Font(None, 96)
        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Cálculos de layout
        self._calculate_layout()
    
    def _calculate_layout(self):
        """Calcula posiciones de las 4 cuerdas"""
        self.string_y_positions = {}
        self.string_height = (WINDOW_HEIGHT - 200) // len(self.STRINGS)
        
        for idx, string_name in enumerate(self.STRINGS):
            y = 100 + (idx * self.string_height)
            self.string_y_positions[string_name] = y
    
    def load_tablature(self, tablature_name: str) -> bool:
        """
        Carga una tablatura
        
        Args:
            tablature_name (str): Nombre de la tablatura guardada
            
        Returns:
            bool: True si se cargó exitosamente
        """
        print(f"[LOADING] Cargando tablatura: {tablature_name}...")
        
        # Cargar datos JSON
        tab_data = self.tab_manager.load_tablature(tablature_name)
        
        if not tab_data:
            print("[ERROR] Error al cargar tablatura")
            return False
        
        # Convertir a formato UI
        self.current_tablature = self.tab_manager.export_to_ui_format(tab_data)
        
        # Preparar notas
        self._prepare_notes()
        
        print(f"[OK] Tablatura cargada: {self.current_tablature['total_notes']} notas")
        return True
    
    def _prepare_notes(self):
        """Prepara la lista de notas para el juego"""
        if not self.current_tablature:
            return
        
        # Construir lista de todas las notas ordenadas por tiempo
        self.upcoming_notes = []
        
        for string_name in self.STRINGS:
            string_notes = self.current_tablature['strings'][string_name]
            for note in string_notes:
                note['string'] = string_name
                self.upcoming_notes.append(note)
        
        # Ordenar por tiempo de inicio
        self.upcoming_notes.sort(key=lambda n: n['start_time'])
        
        self.note_index = 0
        self.active_notes = []
    def start(self):
        """Inicia el modo juego"""
        if not self.current_tablature:
            print("[ERROR] Ninguna tablatura cargada")
            return False
        
        print("[GAME] Iniciando modo juego...")
        
        # Iniciar detector de notas
        if not self.note_detector.start_detection():
            print("⚠️ No se pudo iniciar detección de audio, continuando sin validación")
        
        self.is_running = True
        self.score = 0
        self.combo = 0
        self.hits = 0
        self.misses = 0
        self.current_time = 0.0
        self.start_time = pygame.time.get_ticks() / 1000.0
        
        self.run()
        return True
    
    def stop(self):
        """Detiene el juego"""
        self.is_running = False
        
        # Detener detector
        self.note_detector.stop_detection()
    
    def run(self):
        """Loop principal del juego"""
        while self.is_running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)
    
    def _handle_events(self):
        """Maneja eventos del usuario"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False
                
                elif event.key == pygame.K_SPACE:
                    self.game_paused = not self.game_paused
                
                # Simular toques de cuerdas para testing
                elif event.key == pygame.K_g:
                    self._simulate_string_hit('G')
                elif event.key == pygame.K_c:
                    self._simulate_string_hit('C')
                elif event.key == pygame.K_e:
                    self._simulate_string_hit('E')
                elif event.key == pygame.K_a:
                    self._simulate_string_hit('A')
    
    def _simulate_string_hit(self, string_name: str):
        """Simula un golpe en una cuerda (para testing)"""
        # Buscar nota activa en esa cuerda
        for note in self.active_notes[:]:
            if note['string'] == string_name:
                # Calcular error de timing
                time_error = abs(self.current_time - note['start_time'])
                
                if time_error < 0.15:  # 150ms de tolerancia
                    self._on_note_hit(note, time_error)
                    self.active_notes.remove(note)
                else:
                    self._on_note_miss(note)
                    self.active_notes.remove(note)
                
                return
    
    def _update(self):
        """Actualiza la lógica del juego"""
        if self.game_paused:
            return
        
        # Actualizar tiempo actual
        self.current_time = (pygame.time.get_ticks() / 1000.0) - self.start_time
        
        # Agregar notas nuevas que ya debería haber comenzado
        while (self.note_index < len(self.upcoming_notes) and 
               self.upcoming_notes[self.note_index]['start_time'] <= self.current_time + 5):
            self.active_notes.append(self.upcoming_notes[self.note_index])
            self.note_index += 1
        
        # Actualizar posición de notas activas
        for note in self.active_notes[:]:
            # Calcular posición x basado en tiempo
            time_until_hit = note['start_time'] - self.current_time
            pixels_until_hit = time_until_hit * self.NOTE_SPEED_PIXELS_PER_SECOND
            note['x'] = self.HIT_ZONE_X + pixels_until_hit
            
            # Detectar notas pasadas (misses)
            if self.current_time > note['end_time']:
                if note not in getattr(self, '_hit_notes', []):
                    self._on_note_miss(note)
                self.active_notes.remove(note)
        
        # Verificar si el juego terminó
        if self.note_index >= len(self.upcoming_notes) and not self.active_notes:
            if self.current_time > (self.upcoming_notes[-1]['end_time'] if self.upcoming_notes else 0):
                self._on_game_end()
    
    def _render(self):
        """Renderiza la pantalla"""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Título y estado
        self._render_header()
        
        # Líneas de cuerdas
        self._render_strings()
        
        # Zona de golpeo
        self._render_hit_zone()
        
        # Notas activas
        self._render_notes()
        
        # HUD (Información)
        self._render_hud()
        
        pygame.display.flip()
    
    def _render_header(self):
        """Renderiza el encabezado con información"""
        if self.current_tablature:
            source = self.current_tablature['source']
            tempo = self.current_tablature['tempo']
            
            header_text = f"{source} | {tempo} BPM | {self.current_time:.1f}s"
            header_surface = self.font_medium.render(header_text, True, TEXT_COLOR)
            self.screen.blit(header_surface, (20, 10))
    
    def _render_strings(self):
        """Renderiza las 4 líneas de cuerdas"""
        for string_name, y in self.string_y_positions.items():
            color = self.STRING_COLORS[string_name]
            
            # Nombre de la cuerda
            string_label = self.font_large.render(string_name, True, color)
            self.screen.blit(string_label, (20, y - 20))
            
            # Línea de la cuerda
            pygame.draw.line(
                self.screen, 
                color, 
                (self.HIT_ZONE_X + self.HIT_ZONE_WIDTH, y),
                (WINDOW_WIDTH, y),
                2
            )
    
    def _render_hit_zone(self):
        """Renderiza la zona de golpeo en la izquierda"""
        # Rectángulo de la zona
        pygame.draw.rect(
            self.screen,
            (200, 200, 200),
            (self.HIT_ZONE_X, 80, self.HIT_ZONE_WIDTH, WINDOW_HEIGHT - 160)
        )
        
        # Línea de referencia
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (self.HIT_ZONE_X, 80),
            (self.HIT_ZONE_X, WINDOW_HEIGHT - 80),
            3
        )
    
    def _render_notes(self):
        """Renderiza las notas activas"""
        for note in self.active_notes:
            x = note['x']
            y = self.string_y_positions[note['string']]
            
            # No renderizar notas fuera de pantalla
            if x < -self.NOTE_WIDTH or x > WINDOW_WIDTH:
                continue
            
            color = self.STRING_COLORS[note['string']]
            
            # Dibuja la nota como un rectángulo
            # La altura depende de la duración de la nota
            note_height = max(20, (note['duration'] * self.NOTE_SPEED_PIXELS_PER_SECOND) / 2)
            
            pygame.draw.rect(
                self.screen,
                color,
                (x, y - note_height // 2, self.NOTE_WIDTH, note_height)
            )
            
            # Borde más oscuro
            pygame.draw.rect(
                self.screen,
                tuple(c // 2 for c in color),
                (x, y - note_height // 2, self.NOTE_WIDTH, note_height),
                2
            )
            
            # Número de traste
            fret_text = self.font_small.render(str(note['fret']), True, (0, 0, 0))
            fret_rect = fret_text.get_rect(center=(x + self.NOTE_WIDTH // 2, y))
            self.screen.blit(fret_text, fret_rect)
    
    def _render_hud(self):
        """Renderiza la información del HUD (puntuación, combo, etc)"""
        hud_y = WINDOW_HEIGHT - 70
        
        # Score
        score_text = f"Score: {self.score}"
        score_surface = self.font_medium.render(score_text, True, (255, 255, 100))
        self.screen.blit(score_surface, (20, hud_y))
        
        # Combo
        combo_text = f"Combo: {self.combo}"
        combo_color = (100, 255, 100) if self.combo > 0 else (255, 100, 100)
        combo_surface = self.font_medium.render(combo_text, True, combo_color)
        self.screen.blit(combo_surface, (20, hud_y + 35))
        
        # Estadísticas
        stats_text = f"Hits: {self.hits} | Misses: {self.misses}"
        stats_surface = self.font_small.render(stats_text, True, TEXT_COLOR)
        self.screen.blit(stats_surface, (WINDOW_WIDTH - 300, hud_y))
        
        # Instrucciones
        if self.game_paused:
            pause_text = "PAUSA - Presiona ESPACIO para continuar"
            pause_surface = self.font_medium.render(pause_text, True, (255, 100, 100))
            pause_rect = pause_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_surface, pause_rect)
        else:
            instructions = "Teclas: G=Cuerda G | C=Cuerda C | E=Cuerda E | A=Cuerda A | ESC=Salir"
            inst_surface = self.font_small.render(instructions, True, (150, 150, 150))
            self.screen.blit(inst_surface, (20, WINDOW_HEIGHT - 25))
    
    def _on_note_hit(self, note, time_error):
        """Se ejecuta cuando se golpea una nota correctamente"""
        # Calcular puntos basado en precisión
        if time_error < 0.05:  # Perfecto
            points = 1000
            feedback = "PERFECT!"
            feedback_color = (0, 255, 0)
        elif time_error < 0.1:  # Bien
            points = 500
            feedback = "GOOD!"
            feedback_color = (100, 255, 100)
        else:  # Ok
            points = 100
            feedback = "OK"
            feedback_color = (255, 255, 100)
        
        self.score += points
        self.combo += 1
        self.hits += 1
        self.max_combo = max(self.max_combo, self.combo)
        
        # Marcar nota como golpeada
        if not hasattr(self, '_hit_notes'):
            self._hit_notes = []
        self._hit_notes.append(note)
        
        print(f"[HIT] {feedback} | +{points} pts | Combo: {self.combo}")
    
    def _on_note_miss(self, note):
        """Se ejecuta cuando se pierde una nota"""
        self.misses += 1
        self.combo = 0
        print(f"[MISS] Traste {note['fret']} en cuerda {note['string']}")
    
    def _on_game_end(self):
        """Se ejecuta cuando el juego termina"""
        self.is_running = False
        
        print("\n" + "="*60)
        print("[GAME END]")
        print("="*60)
        print(f"Score Final: {self.score}")
        print(f"Combo Máximo: {self.max_combo}")
        print(f"Notas Correctas: {self.hits}")
        print(f"Notas Perdidas: {self.misses}")
        print(f"Precisión: {(self.hits / (self.hits + self.misses) * 100):.1f}%")
