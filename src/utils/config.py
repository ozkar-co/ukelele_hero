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

# Frecuencias de las cuerdas del ukulele (afinación estándar)
UKULELE_STRINGS = {
    'G4': 392.00,  # 4ª cuerda
    'C4': 261.63,  # 3ª cuerda  
    'E4': 329.63,  # 2ª cuerda
    'A4': 440.00   # 1ª cuerda
}

# Todas las notas musicales con sus frecuencias (4ª octava)
NOTE_FREQUENCIES = {
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
    'B4': 493.88
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