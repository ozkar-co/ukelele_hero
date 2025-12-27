"""
Análisis de frecuencia usando FFT (Fast Fourier Transform)
"""

import numpy as np
from scipy import signal
import sys
from pathlib import Path

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.config import SAMPLE_RATE, MIN_FREQUENCY, MAX_FREQUENCY


class FrequencyAnalyzer:
    """Analizador de frecuencia para detectar notas musicales"""
    
    def __init__(self, sample_rate=SAMPLE_RATE, window_size=4096):
        self.sample_rate = sample_rate
        self.window_size = window_size
        
        # Crear ventana de Hanning para reducir leakage espectral
        self.window = np.hanning(window_size)
        
        # Frecuencias correspondientes a cada bin de la FFT
        self.freqs = np.fft.rfftfreq(window_size, 1/sample_rate)
        
        # Rango de frecuencias de interés (para ukulele: desde C3 hasta E6)
        self.min_freq = MIN_FREQUENCY
        self.max_freq = MAX_FREQUENCY
        
    def analyze_frequency(self, audio_data):
        """
        Analiza los datos de audio y encuentra la frecuencia dominante
        
        Args:
            audio_data (numpy.array): Datos de audio
            
        Returns:
            dict: {'frequency': float, 'magnitude': float, 'confidence': float}
        """
        if len(audio_data) < self.window_size:
            # Rellenar con ceros si es necesario
            padded_data = np.zeros(self.window_size)
            padded_data[:len(audio_data)] = audio_data
            audio_data = padded_data
        
        # Tomar solo la cantidad necesaria de samples
        audio_data = audio_data[-self.window_size:]
        
        # Aplicar ventana para reducir artifacts
        windowed_data = audio_data * self.window
        
        # Calcular FFT
        fft = np.fft.rfft(windowed_data)
        magnitude_spectrum = np.abs(fft)
        
        # Filtrar por rango de frecuencias de interés
        freq_mask = (self.freqs >= self.min_freq) & (self.freqs <= self.max_freq)
        filtered_spectrum = magnitude_spectrum.copy()
        filtered_spectrum[~freq_mask] = 0
        
        # Encontrar pico de frecuencia
        peak_index = np.argmax(filtered_spectrum)
        peak_frequency = self.freqs[peak_index]
        peak_magnitude = filtered_spectrum[peak_index]
        
        # Calcular confianza basada en la claridad del pico
        confidence = self._calculate_confidence(filtered_spectrum, peak_index)
        
        # Interpolación parabólica para mayor precisión en la frecuencia
        if peak_index > 0 and peak_index < len(filtered_spectrum) - 1:
            refined_frequency = self._parabolic_interpolation(
                filtered_spectrum, peak_index, self.freqs
            )
        else:
            refined_frequency = peak_frequency
        
        return {
            'frequency': refined_frequency,
            'magnitude': peak_magnitude,
            'confidence': confidence,
            'spectrum': magnitude_spectrum  # Para debugging/visualización
        }
    
    def _calculate_confidence(self, spectrum, peak_index, window_size=5):
        """
        Calcula la confianza en la detección de frecuencia
        
        Args:
            spectrum (numpy.array): Espectro de magnitud
            peak_index (int): Índice del pico principal
            window_size (int): Tamaño de ventana alrededor del pico
            
        Returns:
            float: Nivel de confianza (0.0 - 1.0)
        """
        if peak_index == 0:
            return 0.0
        
        peak_value = spectrum[peak_index]
        
        # Calcular promedio de valores alrededor del pico (excluyendo el pico)
        start_idx = max(0, peak_index - window_size)
        end_idx = min(len(spectrum), peak_index + window_size + 1)
        
        surrounding_values = np.concatenate([
            spectrum[start_idx:peak_index],
            spectrum[peak_index + 1:end_idx]
        ])
        
        if len(surrounding_values) == 0:
            return 0.0
        
        avg_surrounding = np.mean(surrounding_values)
        
        # Confianza basada en la relación señal/ruido
        if avg_surrounding == 0:
            confidence = 1.0
        else:
            signal_to_noise = peak_value / avg_surrounding
            confidence = min(signal_to_noise / 10.0, 1.0)  # Normalizar
        
        return confidence
    
    def _parabolic_interpolation(self, spectrum, peak_index, freqs):
        """
        Interpola parabólicamente para obtener una frecuencia más precisa
        
        Args:
            spectrum (numpy.array): Espectro de magnitud
            peak_index (int): Índice del pico
            freqs (numpy.array): Array de frecuencias
            
        Returns:
            float: Frecuencia interpolada
        """
        if peak_index <= 0 or peak_index >= len(spectrum) - 1:
            return freqs[peak_index]
        
        # Valores de los tres puntos alrededor del pico
        y1, y2, y3 = spectrum[peak_index - 1:peak_index + 2]
        
        # Fórmula de interpolación parabólica
        a = (y1 - 2*y2 + y3) / 2
        if a == 0:
            return freqs[peak_index]
        
        vertex_offset = (y1 - y3) / (4 * a)
        
        # Calcular frecuencia interpolada
        freq_resolution = freqs[1] - freqs[0]
        interpolated_freq = freqs[peak_index] + vertex_offset * freq_resolution
        
        return interpolated_freq
    
    def get_harmonic_frequencies(self, fundamental_freq, num_harmonics=5):
        """
        Calcula las frecuencias armónicas de una frecuencia fundamental
        
        Args:
            fundamental_freq (float): Frecuencia fundamental
            num_harmonics (int): Número de armónicos a calcular
            
        Returns:
            list: Lista de frecuencias armónicas
        """
        harmonics = []
        for i in range(1, num_harmonics + 1):
            harmonic_freq = fundamental_freq * i
            if harmonic_freq <= self.max_freq:
                harmonics.append(harmonic_freq)
        
        return harmonics
    
    def set_frequency_range(self, min_freq, max_freq):
        """
        Establece el rango de frecuencias a analizar
        
        Args:
            min_freq (float): Frecuencia mínima en Hz
            max_freq (float): Frecuencia máxima en Hz
        """
        self.min_freq = min_freq
        self.max_freq = max_freq