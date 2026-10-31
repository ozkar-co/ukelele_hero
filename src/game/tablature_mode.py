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
from game.ui.styles import HIT_WINDOW_SECONDS, STRING_ORDER
from game.ui.tablature_view import TablatureView
from game.ui.theme import Theme
from utils.config import *
from music.tablature_manager import TablatureManager


class TablatureGameMode:
    """Modo juego con tablaturas - notas desplazándose horizontalmente"""

    STRINGS = STRING_ORDER
    
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()
        
        # Gestor de tablaturas
        self.tab_manager = TablatureManager()
        
        # Estado del juego
        self.current_tablature = None
        self.is_running = False
        self.game_paused = False
        self.countdown_active = False  # Countdown antes de empezar
        self.countdown_time = 3.0  # Tiempo del countdown en segundos
        self.countdown_remaining = 3.0
        self.silence_time = 1.0  # Segundos de silencio después del countdown (1 seg)
        self.pre_game_total = 4.0  # Total: 3 seg countdown + 1 seg silencio
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
        self.font_countdown = pygame.font.Font(None, 150)
        
        # Vista compartida de cuerdas y notas
        self.view = TablatureView(screen)
        self.theme = Theme()

        # Validación de notas y feedback visual
        self.last_detection = None
        self.feedback_text = ""
        self.feedback_color = TEXT_COLOR
        self.feedback_until = 0.0
        self._last_hit_pitch = None
        self._gap_since_hit = True
    
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

        playable_notes = sum(
            len(notes) for notes in self.current_tablature['strings'].values()
        )
        if playable_notes == 0:
            print("[ERROR] La tablatura no tiene notas tocables en el ukulele")
            return False

        # Preparar notas
        self._prepare_notes()

        print(f"[OK] Tablatura cargada: {playable_notes} notas")
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
        
        # AGREGAR TODAS LAS NOTAS A active_notes DESDE EL INICIO
        # Esto permite renderizarlas durante el countdown
        self.active_notes = self.upcoming_notes.copy()
        self.note_index = len(self.active_notes)  # Todas las notas ya están cargadas
        
        # Control de pausa
        self.pause_start_time = None  # Momento en que se pausó

    def start(self):
        """Inicia el modo juego"""
        if not self.current_tablature:
            print("[ERROR] Ninguna tablatura cargada")
            return False
        
        print("[GAME] Iniciando modo juego...")

        # Reiniciar las notas por si se vuelve a iniciar el mismo modo
        self._prepare_notes()

        # Iniciar detector de notas
        if not self.note_detector.start_detection():
            print("⚠️ No se pudo iniciar detección de audio, continuando sin validación")
        
        self.is_running = True
        self.countdown_active = True  # Activar countdown
        self.countdown_remaining = 3.0
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.hits = 0
        self.misses = 0
        self.current_time = 0.0
        self.start_time = pygame.time.get_ticks() / 1000.0
        self.last_detection = None
        self.feedback_text = ""
        self.feedback_until = 0.0
        self._last_hit_pitch = None
        self._gap_since_hit = True

        try:
            self.run()
        finally:
            self.stop()
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
                    
                    if self.game_paused:
                        # Guardar el tiempo de pausa
                        self.pause_start_time = pygame.time.get_ticks() / 1000.0
                    else:
                        # Reanudar: Ajustar start_time para mantener current_time
                        if self.pause_start_time is not None:
                            pause_duration = (pygame.time.get_ticks() / 1000.0) - self.pause_start_time
                            self.start_time += pause_duration
                            self.pause_start_time = None
    
    def _update(self):
        """Actualiza la lógica del juego"""
        if self.game_paused:
            return

        # Calcular tiempo según si estamos en countdown o en juego
        elapsed = (pygame.time.get_ticks() / 1000.0) - self.start_time

        if self.countdown_active:
            self.current_time = elapsed - self.pre_game_total

            if elapsed >= self.pre_game_total:
                self.countdown_active = False
                self.start_time = pygame.time.get_ticks() / 1000.0
                self.current_time = 0.0
            return

        self.current_time = elapsed

        # Validar la nota que está sonando contra las notas de la zona de golpeo
        detection = self.note_detector.update()
        self.last_detection = detection
        if detection is None:
            self._gap_since_hit = True
        else:
            self._try_hit(detection)

        # Las notas que pasan su ventana sin ser tocadas cuentan como fallo
        remaining = []
        for note in self.active_notes:
            if self.current_time > note['start_time'] + HIT_WINDOW_SECONDS:
                self._on_note_miss(note)
            else:
                remaining.append(note)
        self.active_notes = remaining

        if not self.active_notes and self.upcoming_notes:
            last_note_end = self.upcoming_notes[-1]['end_time']
            if self.current_time > last_note_end:
                self._on_game_end()

    def _try_hit(self, detection):
        """Busca una nota de la zona de golpeo que coincida con la detección."""
        detected_note = detection.get('note')
        if not detected_note:
            return

        candidates = [
            note for note in self.active_notes
            if note['note'] == detected_note
            and abs(self.current_time - note['start_time']) <= HIT_WINDOW_SECONDS
        ]
        if not candidates:
            return

        note = min(
            candidates,
            key=lambda candidate: abs(self.current_time - candidate['start_time']),
        )

        # Evitar que una nota sostenida acierte dos notas seguidas del mismo pitch.
        if note['pitch'] == self._last_hit_pitch and not self._gap_since_hit:
            return

        time_error = self.current_time - note['start_time']
        self._on_note_hit(note, abs(time_error), time_error)
        self._last_hit_pitch = note['pitch']
        self._gap_since_hit = False
        self.active_notes.remove(note)
    
    def _render(self):
        """Renderiza la pantalla"""
        if not self.theme.draw_background(
            self.screen, "backgrounds/game.png", dim=110
        ):
            self.screen.fill(BACKGROUND_COLOR)
        self._render_header()
        self.view.draw(self.active_notes, self.current_time)
        self._render_hud()
        pygame.display.flip()

    def _render_header(self):
        """Renderiza el encabezado con información"""
        if not self.current_tablature:
            return

        header_text = (
            f"{self.current_tablature['source']} | "
            f"{self.current_tablature['tempo']} BPM | "
            f"{self.current_time:.1f}s"
        )
        self.theme.draw_text(
            self.screen,
            header_text,
            self.font_medium,
            TEXT_COLOR,
            topleft=(20, 10),
        )

    def _render_hud(self):
        """Renderiza la información del HUD (puntuación, combo, etc)"""
        self.theme.draw_scrim(
            self.screen,
            pygame.Rect(0, WINDOW_HEIGHT - 170, WINDOW_WIDTH, 170),
            alpha=145,
            color=(8, 18, 22),
        )

        # Mostrar countdown si está activo
        if self.countdown_active:
            # Mostrar números 3, 2, 1 basados en current_time
            # current_time va de -4 a 0 durante countdown
            countdown_value = int(-self.current_time)
            
            if 1 <= countdown_value <= 3:
                countdown_text = self.font_countdown.render(str(countdown_value), True, (255, 100, 100))
                countdown_rect = countdown_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(countdown_text, countdown_rect)
        
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

        detected_text = (
            f"Escucho: {self.last_detection['note']}"
            if self.last_detection else "Escucho: -"
        )
        detected_surface = self.font_small.render(detected_text, True, TEXT_COLOR)
        self.screen.blit(detected_surface, (WINDOW_WIDTH - 300, hud_y + 35))

        if self.feedback_text and pygame.time.get_ticks() / 1000.0 < self.feedback_until:
            feedback_surface = self.font_large.render(
                self.feedback_text, True, self.feedback_color
            )
            feedback_rect = feedback_surface.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 130)
            )
            self.screen.blit(feedback_surface, feedback_rect)

        # Instrucciones
        if self.game_paused:
            pause_text = "PAUSA - Presiona ESPACIO para continuar"
            pause_surface = self.font_medium.render(pause_text, True, (255, 100, 100))
            pause_rect = pause_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_surface, pause_rect)
        else:
            self.theme.draw_text(
                self.screen,
                "ESPACIO=Pausa | ESC=Salir",
                self.font_small,
                (190, 200, 195),
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 14),
            )
    
    def _on_note_hit(self, note, abs_time_error, signed_time_error):
        """Se ejecuta cuando se golpea una nota correctamente"""
        if abs_time_error < 0.05:
            points = 1000
            feedback = "PERFECT!"
            feedback_color = (0, 255, 0)
        elif abs_time_error < 0.1:
            points = 500
            feedback = "GOOD!"
            feedback_color = (100, 255, 100)
        else:
            points = 100
            feedback = "OK"
            feedback_color = (255, 255, 100)

        self.score += points
        self.combo += 1
        self.hits += 1
        self.max_combo = max(self.max_combo, self.combo)

        self.feedback_text = feedback
        self.feedback_color = feedback_color
        self.feedback_until = pygame.time.get_ticks() / 1000.0 + 0.6

        print(
            f"[HIT] {feedback} | {signed_time_error:+.3f}s | "
            f"+{points} pts | Combo: {self.combo}"
        )

    def _on_note_miss(self, note):
        """Se ejecuta cuando se pierde una nota"""
        self.misses += 1
        self.combo = 0
        self.feedback_text = "MISS"
        self.feedback_color = (255, 100, 100)
        self.feedback_until = pygame.time.get_ticks() / 1000.0 + 0.5
        print(f"[MISS] Traste {note['fret']} en cuerda {note['string']}")

    def _on_game_end(self):
        """Se ejecuta cuando el juego termina"""
        self.is_running = False

        total = self.hits + self.misses
        precision = (self.hits / total * 100) if total else 0.0

        print("\n" + "=" * 60)
        print("[GAME END]")
        print("=" * 60)
        print(f"Score Final: {self.score}")
        print(f"Combo Maximo: {self.max_combo}")
        print(f"Notas Correctas: {self.hits}")
        print(f"Notas Perdidas: {self.misses}")
        print(f"Precision: {precision:.1f}%")
