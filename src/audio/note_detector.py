"""
Detector de notas musicales basado en análisis de frecuencia
"""

import sys
from pathlib import Path

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from audio.microphone import MicrophoneCapture
from audio.frequency_analyzer import FrequencyAnalyzer
from utils.helpers import frequency_to_note, get_tuning_status
from utils.config import MIN_VOLUME_THRESHOLD
import time


class NoteDetector:
    """Detector de notas musicales en tiempo real"""
    
    def __init__(self):
        self.microphone = MicrophoneCapture()
        self.analyzer = FrequencyAnalyzer()
        
        self.is_detecting = False
        self.current_note = None
        self.current_frequency = 0.0
        self.current_confidence = 0.0
        self.current_deviation = 0.0
        
        # Filtros para suavizar detección
        self.detection_history = []
        self.history_size = 5
        
    def start_detection(self):
        """Inicia la detección de notas"""
        success = self.microphone.start_capture()
        if success:
            self.is_detecting = True
            print("Detector de notas iniciado")
        return success
    
    def stop_detection(self):
        """Detiene la detección de notas"""
        self.is_detecting = False
        self.microphone.stop_capture()
        print("Detector de notas detenido")
    
    def update(self):
        """
        Actualiza la detección de notas (llamar en el bucle principal)
        
        Returns:
            dict: Información de la nota detectada o None
        """
        if not self.is_detecting:
            return None
        
        # Obtener datos de audio
        audio_data = self.microphone.get_audio_data()
        
        # Verificar volumen mínimo
        volume = self.microphone.get_volume_level()
        if volume < MIN_VOLUME_THRESHOLD:
            self._reset_detection()
            return None
        
        # Analizar frecuencia
        analysis = self.analyzer.analyze_frequency(audio_data)
        frequency = analysis['frequency']
        confidence = analysis['confidence']
        
        # Filtrar detecciones con baja confianza
        if confidence < 0.3:  # Umbral ajustable
            self._reset_detection()
            return None
        
        # Convertir frecuencia a nota
        note, deviation = frequency_to_note(frequency)
        if note is None:
            self._reset_detection()
            return None
        
        # Agregar a historial para suavizado
        self.detection_history.append({
            'note': note,
            'frequency': frequency,
            'confidence': confidence,
            'deviation': deviation
        })
        
        # Mantener historial de tamaño fijo
        if len(self.detection_history) > self.history_size:
            self.detection_history.pop(0)
        
        # Determinar nota más probable del historial
        note_result = self._get_most_likely_note()
        
        # Actualizar estado actual
        if note_result:
            self.current_note = note_result['note']
            self.current_frequency = note_result['frequency']
            self.current_confidence = note_result['confidence']
            self.current_deviation = note_result['deviation']
            
            return {
                'note': self.current_note,
                'frequency': self.current_frequency,
                'confidence': self.current_confidence,
                'deviation': self.current_deviation,
                'tuning_status': get_tuning_status(self.current_deviation),
                'volume': volume
            }
        
        return None
    
    def _reset_detection(self):
        """Resetea el estado de detección"""
        self.current_note = None
        self.current_frequency = 0.0
        self.current_confidence = 0.0
        self.current_deviation = 0.0
        self.detection_history.clear()
    
    def _get_most_likely_note(self):
        """
        Determina la nota más probable del historial
        
        Returns:
            dict: Información de la nota más probable
        """
        if not self.detection_history:
            return None
        
        # Contar ocurrencias de cada nota
        note_counts = {}
        note_data = {}
        
        for detection in self.detection_history:
            note = detection['note']
            if note not in note_counts:
                note_counts[note] = 0
                note_data[note] = []
            
            note_counts[note] += detection['confidence']  # Peso por confianza
            note_data[note].append(detection)
        
        # Encontrar la nota con mayor peso
        if not note_counts:
            return None
        
        most_likely_note = max(note_counts.keys(), key=lambda k: note_counts[k])
        
        # Promediar los datos de esa nota
        detections = note_data[most_likely_note]
        
        avg_frequency = sum(d['frequency'] for d in detections) / len(detections)
        avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
        avg_deviation = sum(d['deviation'] for d in detections) / len(detections)
        
        return {
            'note': most_likely_note,
            'frequency': avg_frequency,
            'confidence': avg_confidence,
            'deviation': avg_deviation
        }
    
    def get_current_note_info(self):
        """
        Obtiene información de la nota actual
        
        Returns:
            dict: Información completa de la nota actual
        """
        if not self.current_note:
            return None
        
        return {
            'note': self.current_note,
            'frequency': self.current_frequency,
            'confidence': self.current_confidence,
            'deviation': self.current_deviation,
            'tuning_status': get_tuning_status(self.current_deviation),
            'is_in_tune': abs(self.current_deviation) <= 10  # 10 cents de tolerancia
        }
    
    def calibrate_sensitivity(self, target_note, duration=5.0):
        """
        Calibra la sensibilidad del detector para una nota específica
        
        Args:
            target_note (str): Nota objetivo para calibración
            duration (float): Duración de la calibración en segundos
        """
        print(f"Calibrando para nota {target_note}...")
        print(f"Toca la nota {target_note} durante {duration} segundos")
        
        start_time = time.time()
        detections = []
        
        while time.time() - start_time < duration:
            detection = self.update()
            if detection and detection['note'] == target_note:
                detections.append(detection)
            time.sleep(0.1)
        
        if detections:
            avg_confidence = sum(d['confidence'] for d in detections) / len(detections)
            print(f"Calibración completada. Confianza promedio: {avg_confidence:.2f}")
            return avg_confidence
        else:
            print("No se detectó la nota durante la calibración")
            return None
    
    def get_available_input_devices(self):
        """Obtiene lista de dispositivos de entrada disponibles"""
        return self.microphone.get_input_devices()
    
    def set_input_device(self, device_index):
        """Configura el dispositivo de entrada"""
        self.microphone.set_input_device(device_index)