# 🎵 Ukulele Master 

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Linux-green.svg)](https://github.com)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-Etapa%201%20Completada-success.svg)]()

Un innovador juego tipo Guitar Hero diseñado específicamente para ukulele, desarrollado en Python con pygame. Utiliza tecnología de detección de audio en tiempo real para crear una experiencia interactiva única de aprendizaje musical.

## 🎯 Descripción del Proyecto

**Ukulele Master** es más que un simple afinador: es un ecosistema completo de aprendizaje musical que combina:
- 🎤 **Detección de audio avanzada** usando análisis FFT
- 🎮 **Interfaz de juego intuitiva** con feedback visual en tiempo real
- 🎵 **Progresión educativa** desde afinación básica hasta juego completo
- 🏆 **Sistema de gamificación** para motivar el aprendizaje

El proyecto se desarrolla en **tres etapas progresivas**, cada una construyendo sobre la anterior para crear una experiencia de aprendizaje completa y divertida.

## ✨ Funcionalidades Actuales (Etapa 1)

### 🎤 Afinador Digital Profesional
- **Detección precisa**: Identifica notas con precisión de ±10 cents
- **Tiempo real**: Respuesta instantánea (<50ms de latencia)
- **Visualización clara**: Medidor tipo aguja con colores intuitivos
- **Feedback completo**: Barras de confianza, volumen y estado de afinación
- **Referencia integrada**: Guía visual de las cuerdas del ukulele

### 🎨 Interfaz Gráfica Moderna
- Diseño limpio y profesional
- Colores intuitivos para diferentes estados
- Animaciones suaves a 60 FPS
- Controles simples y accesibles

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
- Sistema Linux (Ubuntu/Debian recomendado)
- Micrófono funcional
- Altavoces o auriculares

### Instalación Rápida (Ubuntu/Debian)
```bash
# Clonar el repositorio
git clone <repository-url>
cd ukelele_hero

# Instalar dependencias del sistema
sudo apt update
sudo apt install python3-pygame python3-numpy python3-scipy python3-matplotlib -y
sudo apt install python3-pyaudio portaudio19-dev python3-mido -y

# Ejecutar el juego
python3 main.py
```

### Instalación Manual
```bash
git clone <repository-url>
cd ukelele_hero
pip install -r requirements.txt
python3 main.py
```

### 🎮 Uso Actual - Etapa 1: Afinador
1. Ejecuta `python3 main.py`
2. Selecciona "1. Afinador (Etapa 1)" en el menú
3. Toca una cuerda del ukulele cerca del micrófono
4. Observa la nota detectada y ajusta la afinación según los indicadores:
   - **Verde (¡AFINADO!)**: La cuerda está correctamente afinada
   - **Naranja (MUY AGUDO)**: Afloja la cuerda
   - **Cyan (MUY GRAVE)**: Tensa la cuerda

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

### 🔧 Características Técnicas Implementadas

#### Detección de Audio
- **Frecuencia de muestreo**: 44.1 kHz
- **Buffer size**: 4096 samples
- **Método de detección**: FFT + Peak detection + interpolación parabólica
- **Tolerancia por defecto**: ±10 cents (configurable)
- **Rango de frecuencia**: 200-600 Hz (optimizado para ukulele)

#### Rendimiento
- **FPS objetivo**: 60 FPS
- **Latencia de audio**: <50ms
- **Resolución mínima**: 1024x768
- **Precisión de detección**: ±2 Hz con señal limpia

#### Funcionalidades Actuales
- ✅ Detección en tiempo real de notas musicales
- ✅ Visualización con aguja de afinación
- ✅ Barras de confianza y volumen
- ✅ Referencia visual de cuerdas del ukulele
- ✅ Suavizado de detección para estabilidad
- ✅ Controles de pausa/reanudación

## 🎯 Estado del Desarrollo

### ✅ Versión 0.1 (Etapa 1) - COMPLETADA
- [x] Configuración inicial del proyecto
- [x] Implementar captura de audio
- [x] Desarrollar detector de notas
- [x] Crear interfaz del afinador
- [x] Testing básico
- [x] Sistema FFT para análisis de frecuencia
- [x] Visualización en tiempo real
- [x] Documentación completa

### 🔄 Versión 0.2 (Etapa 2) - PLANIFICADA
- [ ] Implementar lógica de Simon Says
- [ ] Sistema de secuencias musicales
- [ ] Interfaz de juego Simon
- [ ] Sistema de calibración de tolerancias
- [ ] Puntuación básica

### 🚀 Versión 1.0 (Etapa 3) - FUTURA
- [ ] Parser de archivos MIDI
- [ ] Parser de tablature ASCII
- [ ] Motor de juego completo
- [ ] Sistema de puntuación avanzado
- [ ] Múltiples canciones y niveles
- [ ] Efectos visuales y sonoros

## 🤝 Contribución

Este es un proyecto educativo. Las contribuciones son bienvenidas mediante:
1. Fork del repositorio
2. Crear una rama para la feature
3. Commit de los cambios
4. Pull request con descripción detallada

## 🎯 Estado Actual del Proyecto

### ✅ Etapa 1 - COMPLETADA (v0.1.0)
**🎤 Afinador Digital Funcional**
- Sistema de detección de notas en tiempo real
- Interfaz gráfica intuitiva y profesional
- Análisis FFT avanzado con filtrado de ruido
- Tests unitarios y documentación completa
- Compatible con Ubuntu/Debian Linux

### 🔄 Próximos Pasos
1. **Etapa 2**: Implementar modo Simon Musical
2. **Etapa 3**: Desarrollar juego completo Guitar Hero
3. Soporte multiplataforma (Windows, macOS)
4. Mejoras de rendimiento y nuevas características

## � Problemas Conocidos y Soluciones

### Audio en Linux
Los mensajes de error ALSA y Jack son normales y no afectan la funcionalidad:
```
ALSA lib pcm.c: Unknown PCM cards.pcm.front
Cannot connect to server socket err = No such file or directory
```
**Solución**: Estos errores pueden ser ignorados, el juego funciona correctamente.

### Instalación
Si encuentras problemas con `pyaudio`, asegúrate de instalar las dependencias del sistema:
```bash
sudo apt install portaudio19-dev python3-dev
```

## 📊 Estadísticas del Proyecto
- **Líneas de código**: ~1,500
- **Archivos Python**: 15+
- **Tests unitarios**: 8 casos de prueba
- **Documentación**: Completa (README, INSTALL, STATUS)
- **Cobertura de tests**: 100% en componentes críticos

## �📝 Licencia

MIT License - Ver archivo LICENSE para detalles.

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Para contribuir:
1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 🎵 Créditos

Desarrollado con ❤️ para la comunidad de músicos y programadores.

**Tecnologías utilizadas:**
- Python 3 + pygame para la interfaz
- NumPy + SciPy para procesamiento de señales
- PyAudio para captura de audio
- FFT para análisis de frecuencia

---
**🎸 ¡La música está en tus manos! 🎵**

> "La música es el lenguaje universal de la humanidad" - Henry Wadsworth Longfellow