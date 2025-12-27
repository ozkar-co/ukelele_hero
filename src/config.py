"""
Archivo principal de configuración del proyecto
"""

__version__ = "0.1.0"
__author__ = "Ukulele Master Team"
__description__ = "Un juego tipo Guitar Hero para ukulele con detección de notas en tiempo real"

# Metadatos del proyecto
PROJECT_NAME = "Ukulele Master"
PROJECT_VERSION = __version__
PROJECT_DESCRIPTION = __description__

# Estado del desarrollo
DEVELOPMENT_STAGE = "Etapa 1: Afinador"
FEATURES_COMPLETED = [
    "[OK] Sistema de captura de audio desde micrófono",
    "[OK] Análisis de frecuencia usando FFT",
    "[OK] Detección de notas musicales",
    "[OK] Interfaz gráfica del afinador",
    "[OK] Visualización de estado de afinación",
    "[OK] Tests unitarios básicos"
]

FEATURES_PLANNED = [
    "[PENDING] Etapa 2: Modo Simon Musical",
    "[PENDING] Etapa 3: Juego completo Guitar Hero",
    "[PENDING] Sistema de puntuación",
    "[PENDING] Carga de canciones MIDI",
    "[PENDING] Parser de tablature ASCII",
    "🔄 Múltiples niveles de dificultad"
]

# Información técnica
SUPPORTED_PLATFORMS = ["Linux Ubuntu/Debian"]
PYTHON_VERSION = "3.8+"
DEPENDENCIES = [
    "pygame >= 2.5.0",
    "numpy >= 1.24.0", 
    "sounddevice >= 0.4.5",
    "scipy >= 1.10.0",
    "mido >= 1.2.10"
]