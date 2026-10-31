# Pipeline MIDI y variantes

El generador (`tools/create_tablature.py`) es una herramienta de depuración:
produce los JSON que carga el juego y no forma parte del runtime.

## Flujo

```
MIDI -> pista -> notas -> recorte de silencios -> octava automática
     -> normal (todas las notas tocables)
     -> easy (melodía monofónica simplificada)
     -> JSON separados
```

Cada variante se guarda en un archivo propio:

```
cancion_track0_oct+1_normal.json
cancion_track0_oct+1_easy.json
```

Los metadatos incluyen `preset`, `source_notes`, `playable_metrics` y, en easy,
`processing` con el detalle del proceso aplicado.

La variante normal conserva todas las notas tocables. Todavía no optimiza
voicings de acordes: dos notas de un mismo acorde pueden caer en la misma
cuerda si el MIDI original es polifónico. La variante easy evita ese problema.

## Octava automática

`MIDILoader.adjust_to_ukulele_range` prueba 0, -1, +1, -2 y +2 octavas. Para
cada una calcula:

- cobertura de ataques (onsets) que quedan tocables;
- proporción de notas tocables;
- traste mediano;
- proporción de trastes altos (≥8).

Gana la mejor puntuación; en empate no transpone. Después se descartan las
notas fuera de C4–E6 o de los 20 trastes. En el MIDI de guitarra de prueba este
criterio elige **+1**: +0 perdía la mayor parte de la canción y +2 subía
demasiado el traste mediano.

## Simplificación easy

`src/music/simplifier.py` aplica, en orden:

1. **Skyline**: nota más aguda de cada ataque.
2. **Filtro de valles**: elimina notas claramente por debajo de sus vecinas
   (acompañamiento de arpegios).
3. **Limitación por pulso**: como máximo una nota por negra.
4. **Filtro de rango**: deja solo notas tocables en GCEA.

Es una heurística, no una separación real de voces. El modo Escucha permite
comparar normal y easy antes de dar una tablatura por buena.

## Limitación conocida: separar acompañamiento

Separar melodía y acompañamiento de una pista de guitarra con arpegios es un
problema fuera del alcance actual. En el MIDI de prueba:

- hay una sola pista;
- 105 de 207 ataques tienen 2 notas y 10 tienen 3;
- la melodía y el acompañamiento comparten la misma pista;
- todas las notas tienen la misma velocidad (72), así que la dinámica no ayuda;
- no hay notas cortas que puedan descartarse como adornos.

El skyline y el filtro de valles son aproximaciones. Para futuras canciones es
preferible usar MIDI con la melodía en una pista separada, o sin acompañamiento.
