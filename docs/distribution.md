# Distribución

## Makefile

| Target | Función |
|---|---|
| `make fetch` | Descarga wheels a `wheelhouse/` (requiere red) |
| `make config` | Crea `.venv/` e instala desde `wheelhouse/` |
| `make test` | Ejecuta los tests |
| `make clean` | Borra `.venv/`, `build/` y `dist/` |
| `make dist` | Genera el bundle portable |

`wheelhouse/` es específico de la máquina y de la versión de Python; está
excluido de git y se reconstruye con `make fetch`.

## Bundle

`make dist` usa PyInstaller en modo **onedir** porque numpy, scipy y pygame
son binarios grandes. Salida:

```
dist/ukelele_hero/
  ukelele_hero
  assets/
  docs/
  README.md
  _internal/
```

La carpeta completa se copia a otra máquina Linux con la misma arquitectura.
No hace falta Python ni las dependencias, pero sí PortAudio en el sistema
destino.

`assets/` queda junto al ejecutable. Las tablaturas y los perfiles de
calibración nuevos se escriben ahí, así que el bundle debe estar en una
carpeta con permisos de escritura.

## Documentación

El bundle incluye `README.md` y `docs/` para que la copia portable siga
teniendo instrucciones.
