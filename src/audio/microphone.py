"""
Captura de audio desde el micrófono
"""

import pyaudio
import numpy as np
import threading
import time
from ..utils.config import SAMPLE_RATE, BUFFER_SIZE, CHANNELS


class MicrophoneCapture:
    """Clase para capturar audio desde el micrófono"""
    
    def __init__(self, sample_rate=SAMPLE_RATE, buffer_size=BUFFER_SIZE, channels=CHANNELS):
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.channels = channels
        
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        
        # Buffer circular para almacenar datos de audio
        self.audio_buffer = np.zeros(buffer_size * 4)  # Buffer más grande para análisis
        self.buffer_lock = threading.Lock()
        
        # Thread para captura continua
        self.capture_thread = None
        
    def start_capture(self):
        """Inicia la captura de audio"""
        try:
            # Configurar stream de audio
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.buffer_size,
                stream_callback=self._audio_callback
            )
            
            self.is_recording = True
            self.stream.start_stream()
            print("Captura de audio iniciada")
            
        except Exception as e:
            print(f"Error al iniciar captura de audio: {e}")
            return False
            
        return True
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback para procesar datos de audio entrantes"""
        if status:
            print(f"Status de audio: {status}")
        
        # Convertir datos a array numpy
        audio_data = np.frombuffer(in_data, dtype=np.float32)
        
        # Actualizar buffer circular
        with self.buffer_lock:
            # Desplazar datos existentes
            self.audio_buffer[:-len(audio_data)] = self.audio_buffer[len(audio_data):]
            # Agregar nuevos datos
            self.audio_buffer[-len(audio_data):] = audio_data
        
        return (None, pyaudio.paContinue)
    
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
            self.stream.stop_stream()
            self.stream.close()
            
        if self.audio:
            self.audio.terminate()
            
        print("Captura de audio detenida")
    
    def get_input_devices(self):
        """Obtiene lista de dispositivos de entrada disponibles"""
        devices = []
        
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels'],
                    'sample_rate': device_info['defaultSampleRate']
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
        if self.stream:
            self.stream = self.audio.open(
                format=pyaudio.paFloat32,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.buffer_size,
                stream_callback=self._audio_callback
            )
            
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