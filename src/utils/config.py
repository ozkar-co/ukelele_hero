"""
Configuración del juego Ukulele Master
"""

# Configuración de ventana
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
WINDOW_TITLE = "Ukulele Master"
FPS = 60

# Configuración de audio
SAMPLE_RATE = 44100
BUFFER_SIZE = 4096
CHANNELS = 1

# Configuración de detección de notas
NOTE_TOLERANCE_CENTS = 10  # Tolerancia en cents (100 cents = 1 semitono)
MIN_VOLUME_THRESHOLD = 0.01  # Umbral mínimo de volumen para detectar nota

# Rango de frecuencias para análisis (Hz)
MIN_FREQUENCY = 130    # C3 - nota más grave esperada
MAX_FREQUENCY = 1320   # E6 - nota más aguda (armónicos)

# Frecuencias de las cuerdas del ukulele (afinación estándar)
UKULELE_STRINGS = {
    'G4': 392.00,  # 4ª cuerda
    'C4': 261.63,  # 3ª cuerda  
    'E4': 329.63,  # 2ª cuerda
    'A4': 440.00   # 1ª cuerda
}

# Todas las notas musicales con sus frecuencias (3ª, 4ª y 5ª octava)
NOTE_FREQUENCIES = {
    # 3ª octava (para trastes más graves)
    'C3': 130.81,
    'C#3': 138.59,
    'D3': 146.83,
    'D#3': 155.56,
    'E3': 164.81,
    'F3': 174.61,
    'F#3': 185.00,
    'G3': 196.00,
    'G#3': 207.65,
    'A3': 220.00,
    'A#3': 233.08,
    'B3': 246.94,
    
    # 4ª octava (notas principales del ukulele)
    'C4': 261.63,
    'C#4': 277.18,
    'D4': 293.66,
    'D#4': 311.13,
    'E4': 329.63,
    'F4': 349.23,
    'F#4': 369.99,
    'G4': 392.00,
    'G#4': 415.30,
    'A4': 440.00,
    'A#4': 466.16,
    'B4': 493.88,
    
    # 5ª octava (trastes agudos y armónicos)
    'C5': 523.25,
    'C#5': 554.37,
    'D5': 587.33,
    'D#5': 622.25,
    'E5': 659.25,
    'F5': 698.46,
    'F#5': 739.99,
    'G5': 783.99,
    'G#5': 830.61,
    'A5': 880.00,
    'A#5': 932.33,
    'B5': 987.77,
    
    # 6ª octava (armónicos muy agudos)
    'C6': 1046.50,
    'C#6': 1108.73,
    'D6': 1174.66,
    'D#6': 1244.51,
    'E6': 1318.51
}

# Colores (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Colores del juego
BACKGROUND_COLOR = BLACK
TEXT_COLOR = WHITE
HIGHLIGHT_COLOR = YELLOW
SUCCESS_COLOR = GREEN
ERROR_COLOR = RED

# Configuración de fuentes
FONT_SMALL = 18
FONT_MEDIUM = 24
FONT_LARGE = 36
FONT_XLARGE = 48

# Configuración del juego Simon
SIMON_SEQUENCE_START_LENGTH = 3
SIMON_SEQUENCE_INCREMENT = 1
SIMON_NOTE_DISPLAY_TIME = 1000  # ms
SIMON_GAP_TIME = 500  # ms