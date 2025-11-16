# 🎵 Ukulele Master 

Un juego tipo Guitar Hero diseñado específicamente para ukulele, desarrollado en Python con pygame. El juego detecta las notas tocadas en tiempo real a través del micrófono y proporciona una experiencia interactiva de aprendizaje musical.

## 🎯 Descripción del Proyecto

Ukulele Master es un juego educativo que combina la diversión de los juegos de ritmo con el aprendizaje del ukulele. El proyecto se desarrolla en tres etapas progresivas, desde un afinador básico hasta un juego completo con niveles basados en canciones reales.

## 🏗️ Etapas de Desarrollo

### 📊 Etapa 1: Afinador Digital (Prueba de Concepto)
- **Objetivo**: Detectar y mostrar la nota musical tocada en tiempo real
- **Funcionalidades**:
  - Captura de audio desde micrófono
  - Análisis de frecuencia usando FFT
  - Detección de nota musical (C, D, E, F, G, A, B)
  - Display visual de la nota detectada
  - Indicador de afinación (muy bajo, perfecto, muy alto)

### 🎮 Etapa 2: Simon Musical
- **Objetivo**: Juego de secuencias para calibrar tolerancias y entrenar al jugador
- **Funcionalidades**:
  - Reproducción de secuencias de notas
  - Detección de las notas tocadas por el usuario
  - Sistema de puntuación
  - Niveles progresivos de dificultad
  - Ajuste automático de tolerancias de afinación
  - Feedback visual y auditivo

### 🚀 Etapa 3: Juego Completo
- **Objetivo**: Experiencia completa tipo Guitar Hero para ukulele
- **Funcionalidades**:
  - Carga de canciones desde archivos MIDI
  - Parser de tablature (formato ASCII)
  - Timeline visual con notas descendentes
  - Sistema de puntuación avanzado
  - Múltiples niveles de dificultad
  - Efectos visuales y sonoros
  - Modo práctica y modo competición

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje principal
- **pygame**: Motor de juego y gráficos
- **numpy**: Análisis matemático de audio
- **pyaudio**: Captura de audio del micrófono
- **scipy**: Procesamiento de señales (FFT)
- **mido**: Manejo de archivos MIDI (Etapa 3)
- **pretty_midi**: Análisis avanzado de MIDI (Etapa 3)

## 📁 Estructura del Proyecto

```
ukelele_hero/
├── README.md
├── requirements.txt
├── main.py
├── src/
│   ├── __init__.py
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── microphone.py      # Captura de audio
│   │   ├── frequency_analyzer.py  # Análisis FFT
│   │   └── note_detector.py   # Detección de notas
│   ├── game/
│   │   ├── __init__.py
│   │   ├── tuner_mode.py      # Etapa 1: Afinador
│   │   ├── simon_mode.py      # Etapa 2: Simon
│   │   ├── hero_mode.py       # Etapa 3: Juego completo
│   │   └── ui/
│   │       ├── __init__.py
│   │       ├── screens.py
│   │       └── components.py
│   ├── music/
│   │   ├── __init__.py
│   │   ├── midi_parser.py     # Análisis de MIDI
│   │   ├── tab_parser.py      # Parser de tablature
│   │   └── note_mapping.py    # Mapeo de notas del ukulele
│   └── utils/
│       ├── __init__.py
│       ├── config.py          # Configuración del juego
│       └── helpers.py         # Funciones auxiliares
├── assets/
│   ├── images/
│   ├── sounds/
│   └── fonts/
├── songs/
│   ├── midi/
│   └── tabs/
└── tests/
    ├── __init__.py
    ├── test_audio.py
    ├── test_game.py
    └── test_music.py
```

## 🎵 Configuración del Ukulele

El juego está configurado para la afinación estándar del ukulele:
- **4ª cuerda (G)**: G4 (392 Hz)
- **3ª cuerda (C)**: C4 (261 Hz) 
- **2ª cuerda (E)**: E4 (329 Hz)
- **1ª cuerda (A)**: A4 (440 Hz)

## 🚀 Instalación y Uso

### Prerrequisitos
- Python 3.8 o superior
- Micrófono funcional
- Altavoces o auriculares

### Instalación
```bash
git clone <repository-url>
cd ukelele_hero
pip install -r requirements.txt
```

### Ejecución
```bash
python main.py
```

## 🎮 Controles

- **Espacio**: Pausar/Reanudar
- **ESC**: Menú principal
- **Enter**: Confirmar selección
- **Flechas**: Navegación en menús
- **R**: Reiniciar nivel actual

## 🔧 Configuración

El archivo `src/utils/config.py` contiene la configuración personalizable:
- Sensibilidad del micrófono
- Tolerancia de afinación
- Volumen de efectos de sonido
- Resolución de pantalla
- FPS del juego

## 📊 Características Técnicas

### Detección de Audio
- **Frecuencia de muestreo**: 44.1 kHz
- **Buffer size**: 4096 samples
- **Método de detección**: FFT + Peak detection
- **Tolerancia por defecto**: ±10 cents

### Rendimiento
- **FPS objetivo**: 60 FPS
- **Latencia de audio**: <50ms
- **Resolución mínima**: 800x600

## 🎯 Roadmap de Desarrollo

### Versión 0.1 (Etapa 1)
- [x] Configuración inicial del proyecto
- [ ] Implementar captura de audio
- [ ] Desarrollar detector de notas
- [ ] Crear interfaz del afinador
- [ ] Testing básico

### Versión 0.2 (Etapa 2)
- [ ] Implementar lógica de Simon Says
- [ ] Sistema de secuencias musicales
- [ ] Interfaz de juego Simon
- [ ] Sistema de calibración de tolerancias

### Versión 1.0 (Etapa 3)
- [ ] Parser de archivos MIDI
- [ ] Parser de tablature ASCII
- [ ] Motor de juego completo
- [ ] Sistema de puntuación avanzado
- [ ] Múltiples canciones y niveles

## 🤝 Contribución

Este es un proyecto educativo. Las contribuciones son bienvenidas mediante:
1. Fork del repositorio
2. Crear una rama para la feature
3. Commit de los cambios
4. Pull request con descripción detallada

## 📝 Licencia

MIT License - Ver archivo LICENSE para detalles.

## 🎵 Créditos

Desarrollado con ❤️ para la comunidad de músicos y programadores.

---
**¡Que comience la música! 🎸🎵**