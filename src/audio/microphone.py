"""
Captura de audio desde el micrófono
"""

import sounddevice as sd
import numpy as np
import threading
import time
import sys
from pathlib import Path

# Agregar src al path para imports absolutos
current_dir = Path(__file__).parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from utils.config import SAMPLE_RATE, BUFFER_SIZE, CHANNELS


class MicrophoneCapture:
    """Clase para capturar audio desde el micrófono"""
    
    def __init__(self, sample_rate=SAMPLE_RATE, buffer_size=BUFFER_SIZE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        
        self.stream = None
        self.is_recording = False
        self.device_index = None
        
        # Buffer circular para almacenar datos de audio
        self.audio_buffer = np.zeros(buffer_size * 4)  # Buffer más grande para análisis
        self.buffer_lock = threading.Lock()
        
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback para procesar datos de audio entrantes"""
        if status:
            print(f"Estado de audio: {status}")
        
        # Convertir datos a array numpy (sounddevice ya lo proporciona en float32)
        audio_data = indata[:, 0] if self.channels == 1 else indata.mean(axis=1)
        
        # Actualizar buffer circular
        with self.buffer_lock:
            # Desplazar datos existentes
            self.audio_buffer[:-len(audio_data)] = self.audio_buffer[len(audio_data):]
            # Agregar nuevos datos
            self.audio_buffer[-len(audio_data):] = audio_data
    
    def start_capture(self):
        """Inicia la captura de audio"""
        try:
            # Configurar stream de audio con sounddevice
            self.stream = sd.InputStream(
                device=self.device_index,
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.buffer_size,
                callback=self._audio_callback,
                dtype=np.float32
            )
            
            self.is_recording = True
            self.stream.start()
            print("Captura de audio iniciada")
            
        except Exception as e:
            print(f"Error al iniciar captura de audio: {e}")
            return False
            
        return True
    
    def get_audio_data(self, length=None):
        """
        Obtiene los datos de audio más recientes
        
        Args:
            length (int): Cantidad de samples a obtener (por defecto buffer_size)
            
        Returns:
            numpy.array: Datos de audio
        """
        if length is None:
            length = self.buffer_size
            
        with self.buffer_lock:
            return self.audio_buffer[-length:].copy()
    
    def stop_capture(self):
        """Detiene la captura de audio"""
        self.is_recording = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            
        print("Captura de audio detenida")
    
    def get_input_devices(self):
        """Obtiene lista de dispositivos de entrada disponibles"""
        devices = []
        
        for i, device_info in enumerate(sd.query_devices()):
            if device_info['max_input_channels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['max_input_channels'],
                    'sample_rate': device_info['default_samplerate']
                })
                
        return devices
    
    def set_input_device(self, device_index):
        """
        Configura el dispositivo de entrada
        
        Args:
            device_index (int): Índice del dispositivo
        """
        # Reiniciar stream si está activo
        was_recording = self.is_recording
        if was_recording:
            self.stop_capture()
        
        # Configurar nuevo dispositivo
        self.device_index = device_index
            
        if was_recording:
            self.start_capture()
    
    def get_volume_level(self):
        """
        Obtiene el nivel de volumen actual
        
        Returns:
            float: Nivel de volumen (0.0 - 1.0)
        """
        audio_data = self.get_audio_data()
        return np.sqrt(np.mean(audio_data ** 2))
    
    def is_active(self):
        """Verifica si la captura está activa"""
        return self.is_recording and self.stream and self.stream.is_active()