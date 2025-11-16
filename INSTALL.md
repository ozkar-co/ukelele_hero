# 📋 INSTALACIÓN Y CONFIGURACIÓN

## 📋 Guía de Instalación Completa

### 🐧 Ubuntu/Debian Linux

```bash
# 1. Actualizar el sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependencias del sistema
sudo apt install python3 python3-dev python3-pip -y
sudo apt install python3-pygame python3-numpy python3-scipy python3-matplotlib -y
sudo apt install python3-pyaudio portaudio19-dev -y
sudo apt install python3-mido -y

# 3. Clonar el repositorio
git clone <repository-url>
cd ukelele_hero

# 4. Ejecutar el juego
python3 main.py
```

### 🎤 Configuración de Audio

#### Verificar Micrófono
```bash
# Verificar dispositivos de audio
arecord -l

# Probar grabación (Ctrl+C para detener)
arecord -f cd test.wav

# Reproducir grabación
aplay test.wav
```

#### Problemas Comunes de Audio

**1. Errores ALSA (Normal):**
- Los errores ALSA mostrados son normales en sistemas Linux
- No impiden el funcionamiento del juego
- Para silenciarlos (opcional):
```bash
export ALSA_CARD=0
```

**2. No se detecta micrófono:**
```bash
# Instalar PulseAudio si no está disponible
sudo apt install pulseaudio pulseaudio-utils -y

# Verificar PulseAudio
pulseaudio --check -v
```

**3. Permisos de audio:**
```bash
# Agregar usuario al grupo audio
sudo usermod -a -G audio $USER
# Logout/login para aplicar cambios
```

### 🎵 Configuración del Ukulele

1. **Afinación Estándar:**
   - 4ª cuerda: G4 (392 Hz)
   - 3ª cuerda: C4 (261 Hz)
   - 2ª cuerda: E4 (329 Hz)
   - 1ª cuerda: A4 (440 Hz)

2. **Posicionamiento del Micrófono:**
   - Coloca el micrófono cerca de la caja de resonancia
   - Evita ruido de fondo
   - Distancia recomendada: 20-30 cm

3. **Calibración:**
   - Usa el modo afinador para calibrar
   - Ajusta el volumen del micrófono si es necesario

### 🚀 Uso del Juego

#### Modo Afinador (Etapa 1)
1. Selecciona "1. Afinador" en el menú principal
2. Toca una cuerda del ukulele
3. Observa la nota detectada y el estado de afinación
4. Ajusta la tensión de la cuerda según las indicaciones

#### Controles del Afinador
- **ESPACIO**: Pausar/Reanudar detección
- **ESC**: Volver al menú principal

### 🔧 Configuración Avanzada

#### Ajustar Sensibilidad
Edita `src/utils/config.py`:
```python
# Tolerancia de afinación (en cents)
NOTE_TOLERANCE_CENTS = 15  # Más tolerante

# Umbral de volumen mínimo
MIN_VOLUME_THRESHOLD = 0.005  # Más sensible
```

#### Dispositivo de Audio Específico
Si tienes múltiples micrófonos, puedes especificar cuál usar:
```python
# En el código del detector de notas
detector.set_input_device(device_index)
```

### 📊 Resolución de Problemas

#### El juego no inicia
```bash
# Verificar instalación de pygame
python3 -c "import pygame; print(pygame.version.ver)"

# Verificar instalación de pyaudio
python3 -c "import pyaudio; print('PyAudio OK')"
```

#### No se detectan notas
1. Verifica que el micrófono esté funcionando
2. Aumenta el volumen del micrófono en el sistema
3. Reduce el ruido de fondo
4. Toca las cuerdas con más fuerza

#### Detección imprecisa
1. Afina el ukulele correctamente primero
2. Toca una cuerda a la vez
3. Evita tocar múltiples cuerdas simultáneamente
4. Ajusta la distancia del micrófono

### 📈 Rendimiento

#### Optimización
- Cierra aplicaciones que usen audio
- Usa auriculares para evitar retroalimentación
- Mantén el sistema actualizado

#### Recursos del Sistema
- **RAM mínima**: 1 GB
- **CPU**: Cualquier procesador moderno
- **Audio**: Micrófono integrado o externo

### 🆘 Soporte

Si tienes problemas:
1. Verifica que todas las dependencias estén instaladas
2. Revisa los logs en la terminal
3. Prueba con diferentes micrófonos
4. Consulta la documentación de tu distribución Linux para configuración de audio

### 📝 Logs Útiles

Para debug avanzado:
```bash
# Ejecutar con información de debug de audio
ALSA_DEBUG=1 python3 main.py

# Ver dispositivos de audio detallados
cat /proc/asound/cards
```