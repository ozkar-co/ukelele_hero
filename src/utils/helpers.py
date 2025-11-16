"""
Funciones auxiliares para el juego Ukulele Master
"""

import numpy as np
from .config import NOTE_FREQUENCIES, NOTE_TOLERANCE_CENTS


def frequency_to_note(frequency):
    """
    Convierte una frecuencia en Hz a la nota musical más cercana
    
    Args:
        frequency (float): Frecuencia en Hz
        
    Returns:
        tuple: (nota, desviacion_en_cents)
    """
    if frequency <= 0:
        return None, 0
    
    # Calcular la distancia a cada nota conocida
    min_distance = float('inf')
    closest_note = None
    deviation = 0
    
    for note, note_freq in NOTE_FREQUENCIES.items():
        # Calcular distancia en cents (100 cents = 1 semitono)
        distance_cents = 1200 * np.log2(frequency / note_freq)
        abs_distance = abs(distance_cents)
        
        if abs_distance < min_distance:
            min_distance = abs_distance
            closest_note = note
            deviation = distance_cents
    
    # Solo devolver resultado si está dentro de un rango razonable (±50 cents)
    if min_distance <= 50:
        return closest_note, deviation
    else:
        return None, 0


def is_note_in_tune(deviation_cents, tolerance=NOTE_TOLERANCE_CENTS):
    """
    Determina si una nota está afinada dentro de la tolerancia
    
    Args:
        deviation_cents (float): Desviación en cents
        tolerance (float): Tolerancia en cents
        
    Returns:
        bool: True si está afinada
    """
    return abs(deviation_cents) <= tolerance


def get_tuning_status(deviation_cents, tolerance=NOTE_TOLERANCE_CENTS):
    """
    Obtiene el estado de afinación
    
    Args:
        deviation_cents (float): Desviación en cents
        tolerance (float): Tolerancia en cents
        
    Returns:
        str: 'perfect', 'sharp', 'flat'
    """
    if abs(deviation_cents) <= tolerance:
        return 'perfect'
    elif deviation_cents > 0:
        return 'sharp'  # Demasiado agudo
    else:
        return 'flat'   # Demasiado grave


def note_to_frequency(note):
    """
    Convierte una nota musical a su frecuencia en Hz
    
    Args:
        note (str): Nota musical (ej: 'A4', 'C4')
        
    Returns:
        float: Frecuencia en Hz o None si no se encuentra
    """
    return NOTE_FREQUENCIES.get(note, None)


def calculate_volume(audio_data):
    """
    Calcula el volumen RMS de los datos de audio
    
    Args:
        audio_data (numpy.array): Datos de audio
        
    Returns:
        float: Volumen RMS normalizado (0.0 - 1.0)
    """
    if len(audio_data) == 0:
        return 0.0
    
    # Calcular RMS (Root Mean Square)
    rms = np.sqrt(np.mean(audio_data ** 2))
    
    # Normalizar a un rango de 0-1 (ajustable según sea necesario)
    return min(rms * 10, 1.0)


def format_frequency(frequency):
    """
    Formatea una frecuencia para mostrar
    
    Args:
        frequency (float): Frecuencia en Hz
        
    Returns:
        str: Frecuencia formateada
    """
    if frequency < 1000:
        return f"{frequency:.1f} Hz"
    else:
        return f"{frequency/1000:.2f} kHz"


def format_cents(cents):
    """
    Formatea la desviación en cents para mostrar
    
    Args:
        cents (float): Desviación en cents
        
    Returns:
        str: Desviación formateada
    """
    if cents > 0:
        return f"+{cents:.0f}¢"
    else:
        return f"{cents:.0f}¢"