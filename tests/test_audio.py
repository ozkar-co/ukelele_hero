"""
Tests básicos para el sistema de audio
"""

import unittest
import numpy as np
from src.audio.frequency_analyzer import FrequencyAnalyzer
from src.utils.helpers import frequency_to_note, note_to_frequency


class TestFrequencyAnalyzer(unittest.TestCase):
    """Tests para el analizador de frecuencia"""
    
    def setUp(self):
        self.analyzer = FrequencyAnalyzer(sample_rate=44100, window_size=4096)
    
    def test_analyzer_initialization(self):
        """Test de inicialización del analizador"""
        self.assertEqual(self.analyzer.sample_rate, 44100)
        self.assertEqual(self.analyzer.window_size, 4096)
        self.assertIsNotNone(self.analyzer.window)
        self.assertIsNotNone(self.analyzer.freqs)
    
    def test_sine_wave_detection(self):
        """Test de detección de onda seno pura"""
        # Generar onda seno de 440 Hz (A4)
        duration = 0.1  # 100ms
        t = np.linspace(0, duration, int(self.analyzer.sample_rate * duration))
        frequency = 440.0
        amplitude = 0.5
        sine_wave = amplitude * np.sin(2 * np.pi * frequency * t)
        
        # Agregar padding para llegar al tamaño de ventana
        if len(sine_wave) < self.analyzer.window_size:
            padded_wave = np.zeros(self.analyzer.window_size)
            padded_wave[:len(sine_wave)] = sine_wave
            sine_wave = padded_wave
        
        # Analizar
        result = self.analyzer.analyze_frequency(sine_wave)
        
        # Verificar que detecte aproximadamente 440 Hz
        detected_freq = result['frequency']
        self.assertAlmostEqual(detected_freq, frequency, delta=5.0)
        self.assertGreater(result['confidence'], 0.5)


class TestHelpers(unittest.TestCase):
    """Tests para funciones auxiliares"""
    
    def test_frequency_to_note_a4(self):
        """Test conversión de 440 Hz a A4"""
        note, deviation = frequency_to_note(440.0)
        self.assertEqual(note, 'A4')
        self.assertAlmostEqual(deviation, 0.0, delta=0.1)
    
    def test_frequency_to_note_c4(self):
        """Test conversión de ~261.63 Hz a C4"""
        note, deviation = frequency_to_note(261.63)
        self.assertEqual(note, 'C4')
        self.assertAlmostEqual(deviation, 0.0, delta=1.0)
    
    def test_note_to_frequency_a4(self):
        """Test conversión de A4 a frecuencia"""
        freq = note_to_frequency('A4')
        self.assertEqual(freq, 440.0)
    
    def test_note_to_frequency_invalid(self):
        """Test conversión de nota inválida"""
        freq = note_to_frequency('X9')
        self.assertIsNone(freq)
    
    def test_frequency_to_note_sharp(self):
        """Test detección de nota desafinada (aguda)"""
        # 445 Hz debería ser A4 pero ~20 cents aguda
        note, deviation = frequency_to_note(445.0)
        self.assertEqual(note, 'A4')
        self.assertGreater(deviation, 15)  # Debería ser positivo (agudo)
    
    def test_frequency_to_note_flat(self):
        """Test detección de nota desafinada (grave)"""
        # 435 Hz debería ser A4 pero ~20 cents grave
        note, deviation = frequency_to_note(435.0)
        self.assertEqual(note, 'A4')
        self.assertLess(deviation, -15)  # Debería ser negativo (grave)


if __name__ == '__main__':
    unittest.main()