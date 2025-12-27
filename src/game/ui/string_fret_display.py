"""
Display visual representation of ukulele strings and frets
Shows possible frets to play a detected note
"""

import pygame
import sys
from pathlib import Path

# Agregar src al path
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.config import *


class StringFretDisplay:
    """Visual display of ukulele strings with fret positions"""
    
    # Ukulele configuration
    STRINGS = ['G', 'C', 'E', 'A']
    STRING_MIDI_NOTES = {
        'G': 67,  # G4
        'C': 60,  # C4
        'E': 64,  # E4
        'A': 69,  # A4
    }
    
    STRING_COLORS = {
        'G': (100, 200, 100),  # Green
        'C': (100, 150, 255),  # Blue
        'E': (255, 100, 100),  # Red
        'A': (255, 255, 100),  # Yellow
    }
    
    # Visual configuration
    MAX_FRETS = 20  # Maximum fret to display
    FRET_WIDTH = 30
    FRET_HEIGHT = 40
    STRING_SPACING = 80
    
    def __init__(self, screen, x=None, y=50, width=150):
        """
        Initialize string/fret display
        
        Args:
            screen: pygame screen object
            x: x position on screen (default: right side)
            y: y position on screen
            width: width of display area
        """
        self.screen = screen
        
        # Default to right side if not specified
        if x is None:
            x = WINDOW_WIDTH - width - 20
        
        self.x = x
        self.y = y
        self.width = width
        
        # Fonts
        self.font_fret = pygame.font.Font(None, 18)
        self.font_label = pygame.font.Font(None, 16)
        
        # Current detected note
        self.detected_pitch = None
        self.possible_frets = {}  # {string: [frets]}
    
    def update_detected_note(self, midi_pitch):
        """
        Update with detected note and calculate possible frets
        
        Args:
            midi_pitch (int): MIDI note number (0-127)
        """
        self.detected_pitch = midi_pitch
        self.possible_frets = self._calculate_frets(midi_pitch)
    
    def _calculate_frets(self, midi_pitch):
        """
        Calculate which frets can produce the given pitch
        
        Args:
            midi_pitch (int): MIDI note number
            
        Returns:
            dict: {string_name: [fret_numbers]}
        """
        frets = {}
        
        for string_name in self.STRINGS:
            open_string_pitch = self.STRING_MIDI_NOTES[string_name]
            
            # Calculate fret number
            fret = midi_pitch - open_string_pitch
            
            # Check if fret is within valid range (0-20)
            if 0 <= fret <= self.MAX_FRETS:
                frets[string_name] = [fret]
        
        return frets
    
    def update_from_frequency(self, frequency):
        """
        Update with detected frequency and calculate possible frets
        
        Args:
            frequency (float): Audio frequency in Hz
        """
        if frequency <= 0:
            self.detected_pitch = None
            self.possible_frets = {}
            return
        
        # Convert frequency to MIDI pitch
        # MIDI pitch = 12 * log2(f / 440) + 69
        import math
        midi_pitch = round(12 * math.log2(frequency / 440) + 69)
        
        # Clamp to valid MIDI range
        midi_pitch = max(0, min(127, midi_pitch))
        
        self.update_detected_note(midi_pitch)
    
    def draw(self):
        """Draw the string and fret display"""
        # Draw title
        title = self.font_label.render("TRASTES", True, HIGHLIGHT_COLOR)
        self.screen.blit(title, (self.x, self.y))
        
        # Draw each string with only applicable frets
        for idx, string_name in enumerate(self.STRINGS):
            string_y = self.y + 30 + (idx * 50)
            
            # Draw string label
            label = self.font_label.render(string_name, True, self.STRING_COLORS[string_name])
            self.screen.blit(label, (self.x, string_y))
            
            # Draw applicable frets for this string
            self._draw_string_frets(string_name, string_y)
    
    def _draw_string_frets(self, string_name, y):
        """
        Draw only applicable frets for a specific string
        
        Args:
            string_name (str): String identifier ('G', 'C', 'E', 'A')
            y (int): Y position to draw
        """
        possible = self.possible_frets.get(string_name, [])
        
        if not possible:
            # No frets available for this string
            no_fret_text = self.font_fret.render("- - -", True, (100, 100, 100))
            self.screen.blit(no_fret_text, (self.x + 30, y + 5))
        else:
            # Show applicable frets with numbers
            fret_str = " ".join(str(f) for f in possible)
            fret_text = self.font_fret.render(fret_str, True, (0, 255, 0))
            self.screen.blit(fret_text, (self.x + 30, y + 5))
    
    def get_possible_frets_for_string(self, string_name):
        """
        Get possible frets for a specific string
        
        Args:
            string_name (str): String identifier
            
        Returns:
            list: Fret numbers that can play the detected note
        """
        return self.possible_frets.get(string_name, [])
    
    def get_all_possible_frets(self):
        """
        Get all possible frets across all strings
        
        Returns:
            dict: {string_name: [frets]}
        """
        return self.possible_frets.copy()
    
    def has_possible_frets(self):
        """
        Check if there are any possible frets for detected note
        
        Returns:
            bool: True if at least one fret is possible
        """
        return len(self.possible_frets) > 0
