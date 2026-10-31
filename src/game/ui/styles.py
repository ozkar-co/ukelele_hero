"""
Estilos compartidos para las vistas de tablatura.

Un solo lugar para colores de cuerdas, dimensiones de notas, zona de golpeo
y velocidad de desplazamiento.
"""

# Orden visual de la tablatura: A arriba, G abajo.
STRING_ORDER = ("A", "E", "C", "G")

STRING_COLORS = {
    "G": (100, 200, 100),  # Verde
    "C": (100, 150, 255),  # Azul
    "E": (255, 100, 100),  # Rojo
    "A": (255, 255, 100),  # Amarillo
}

LANE_TOP = 100
LANE_BOTTOM_MARGIN = 100

NOTE_WIDTH = 30
NOTE_HEIGHT = 50
NOTE_SPEED_PIXELS_PER_SECOND = 400

HIT_ZONE_X = 150
HIT_ZONE_WIDTH = 40
HIT_WINDOW_SECONDS = 0.20

HIT_ZONE_COLOR = (220, 230, 235)
HIT_ZONE_FILL_ALPHA = 38
HIT_ZONE_LINE_COLOR = (255, 255, 255)
NOTE_TEXT_COLOR = (0, 0, 0)

NOTE_OUTLINE_DIVISOR = 2
